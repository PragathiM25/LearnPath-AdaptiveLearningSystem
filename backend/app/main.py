
from pathlib import Path
import os
from uuid import uuid4
from threading import Lock
from .ml_model import predict_next_success

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from .config import UPLOAD_PATH
from .database import (
    init_db,
    save_document,
    list_documents,
    save_attempt,
    get_attempts,
)
from .schemas import TutorRequest, QuizRequest, QuizSubmission
from .rag import index_pages, retrieve
from .llm import answer_question, generate_quiz
from .analytics import get_performance, get_learning_path

app = FastAPI(
    title="LearnPath API",
    description="Adaptive learning, AI tutoring and knowledge-gap support",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MAX_PDF_BYTES = 20 * 1024 * 1024

# Demo-only quiz session storage. Sessions are lost when the server restarts.
# For production, persist quiz sessions and answer keys in the database.
quiz_sessions = {}
quiz_lock = Lock()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "name": "LearnPath",
        "message": "Adaptive Learning API is running",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "LearnPath API"}


def retrieve_material(query: str):
    passages = retrieve(query)
    sources = []
    seen_sources = set()

    for passage in passages:
        metadata = passage["metadata"]
        source = {
            "document": metadata["document"],
            "page": metadata["page"],
        }
        source_key = (source["document"], source["page"])
        if source_key not in seen_sources:
            sources.append(source)
            seen_sources.add(source_key)

    context = "\n\n".join(
        f"Source: {passage['metadata']['document']}, "
        f"page {passage['metadata']['page']}\n{passage['text']}"
        for passage in passages
    )
    return context, sources


@app.get("/api/documents")
def documents():
    return {"documents": list_documents()}


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "study.pdf").name

    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(400, "Only PDF files are supported.")

    contents = await file.read(MAX_PDF_BYTES + 1)
    if len(contents) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF exceeds the 20 MB limit.")

    if not contents.startswith(b"%PDF"):
        raise HTTPException(400, "The uploaded file is not a valid PDF.")

    stored_name = f"{uuid4().hex}.pdf"
    destination = UPLOAD_PATH / stored_name
    destination.write_bytes(contents)

    try:
        reader = PdfReader(str(destination))
        pages = [(page.extract_text() or "") for page in reader.pages]
        if not any(text.strip() for text in pages):
            destination.unlink(missing_ok=True)
            raise HTTPException(
                422,
                "No selectable text found. Scanned PDFs need OCR first.",
            )

        chunks = index_pages(filename, pages)
        document_id = save_document(filename, str(destination))

        return {
            "id": document_id,
            "filename": filename,
            "pages": len(pages),
            "indexed_chunks": chunks,
            "message": "Study material uploaded and indexed.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            500, f"Could not process PDF: {type(exc).__name__}"
        ) from exc

@app.post("/api/tutor/ask")
def tutor(request: TutorRequest):
    try:
        context, sources = retrieve_material(request.question)
        return {
            "answer": answer_question(request.question, context),
            "sources": sources,
            "grounded_in_uploaded_material": bool(sources),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Tutor request failed: {type(exc).__name__}: {exc}"
        ) from exc

@app.post("/api/quiz/generate")
def create_quiz(request: QuizRequest):
    try:
        context, sources = retrieve_material(request.topic)
        generated = generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.number_of_questions,
            context=context,
        )
    except Exception as exc:
        raise HTTPException(
            502, f"Quiz generation failed: {type(exc).__name__}"
        ) from exc

    session_id = uuid4().hex
    questions = [
        {
            **question,
            "question_id": question.get("question_id") or question["id"],
        }
        for question in generated["questions"]
    ]

    with quiz_lock:
        quiz_sessions[session_id] = {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "questions": questions,
        }

    # Never send the answer key to the browser before submission.
    public_questions = [
        {
            "question_id": question["question_id"],
            "question": question["question"],
            "options": question["options"],
        }
        for question in questions
    ]

    return {
        "session_id": session_id,
        "topic": request.topic,
        "questions": public_questions,
        "sources": generated.get("sources", sources),
    }


@app.post("/api/quiz/submit")
def submit_quiz(request: QuizSubmission, session_id: str):
    with quiz_lock:
        session = quiz_sessions.pop(session_id, None)

    if session is None:
        raise HTTPException(
            404,
            "Quiz session not found or already submitted. Generate a new quiz.",
        )

    questions = session["questions"]
    expected_ids = {q["question_id"] for q in questions}
    supplied_ids = [a.question_id for a in request.answers]

    if (
        len(supplied_ids) != len(expected_ids)
        or len(set(supplied_ids)) != len(supplied_ids)
        or set(supplied_ids) != expected_ids
    ):
        raise HTTPException(
            400, "Submit exactly one answer for every quiz question."
        )

    answer_map = {a.question_id: a.selected_option for a in request.answers}
    feedback = []
    correct_count = 0

    for question in questions:
        selected = answer_map[question["question_id"]]
        correct_index = question["correct_answer"]
        is_correct = selected == correct_index

        if is_correct:
            correct_count += 1

        save_attempt(
            student_id=request.student_id,
            topic=session["topic"],
            question=question["question"],
            correct=is_correct,
            difficulty=session["difficulty"],
        )

        feedback.append({
            "question_id": question["question_id"],
            "correct": is_correct,
            "correct_option": correct_index,
            "explanation": question.get("explanation", ""),
        })

    total = len(questions)
    return {
        "score": correct_count,
        "total": total,
        "accuracy": round(correct_count / total, 3) if total else 0,
        "feedback": feedback,
        "message": (
            "Great work! Keep building your understanding."
            if correct_count / total >= 0.7
            else "Review the explanations and try another practice set."
        ),
    }


@app.get("/api/performance/{student_id}")
def performance(student_id: str):
    return {
        "student_id": student_id,
        "performance": get_performance(student_id),
    }


@app.get("/api/learning-path/{student_id}")
def learning_path(student_id: str):
    return get_learning_path(student_id)


@app.get("/api/student/{student_id}/summary")
def student_summary(student_id: str):
    attempts = get_attempts(student_id)
    total = len(attempts)
    correct = sum(int(a["correct"]) for a in attempts)

    return {
        "student_id": student_id,
        "total_attempts": total,
        "correct_answers": correct,
        "accuracy": round(correct / total, 3) if total else 0,
        "topics": len(set(a["topic"] for a in attempts)),
    }

@app.post("/api/student/predict")
def predict_performance(student_data: dict):
    try:
        return predict_next_success(student_data)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {type(exc).__name__}: {exc}",
        ) from exc