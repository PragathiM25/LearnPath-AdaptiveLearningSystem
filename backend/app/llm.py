
import json
import os
import re

import requests

from .import config as _config


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL", "http://localhost:11434"
).rstrip("/")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def _chat(messages, json_mode=False):
    """Send a chat request to the locally running Ollama model."""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.3,
        },
    }

    if json_mode:
        payload["format"] = "json"

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to Ollama. Start Ollama and check "
            "that it is running at http://localhost:11434."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "Ollama took too long to respond. Try a smaller model "
            "or a shorter prompt."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc


def answer_question(question: str, context: str = "") -> str:
    """Answer a student's question using retrieved study material."""

    context = context.strip() if context else ""

    if context:
        system_prompt = (
            "You are LearnPath, a friendly AI tutor for college students. "
            "Use the supplied study material when it is relevant. "
            "If the material does not contain the answer, say so clearly "
            "and then distinguish any general explanation from the material. "
            "Explain concepts in simple language, use examples, and do not "
            "invent facts or citations."
        )

        user_prompt = (
            f"Study material:\n{context}\n\n"
            f"Student question:\n{question}\n\n"
            "Explain the answer clearly and step by step."
        )
    else:
        system_prompt = (
            "You are LearnPath, a friendly AI tutor for college students. "
            "Explain concepts in simple language with examples. "
            "If you are unsure, say so rather than inventing facts."
        )
        user_prompt = question

    return _chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]).strip()


def generate_quiz(
    topic: str,
    difficulty: str = "medium",
    num_questions: int = 5,
    context: str = "",
) -> dict:
    """Generate a multiple-choice quiz and its answer key."""

    num_questions = max(1, min(int(num_questions), 10))

    instructions = f"""
Create exactly {num_questions} multiple-choice questions for a student.

Topic: {topic}
Difficulty: {difficulty}

Use this study material when provided:
{context or "No specific study material was provided."}

Return valid JSON only, using this structure:
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text",
      "options": [
        "First option",
        "Second option",
        "Third option",
        "Fourth option"
      ],
      "correct_answer": 0,
      "explanation": "Why the correct option is right"
    }}
  ]
}}

Rules:
- Each question must have exactly four options.
- correct_answer must be an integer from 0 to 3.
- The integer identifies the correct option by its zero-based index.
- Questions must be clear, educational, and relevant to the topic.
- Do not include the answer in the question text.
- Return exactly {num_questions} questions.
"""

    content = _chat([
        {
            "role": "system",
            "content": (
                "You create accurate educational multiple-choice quizzes. "
                "Follow the requested JSON structure exactly."
            ),
        },
        {"role": "user", "content": instructions},
    ], json_mode=True)

    try:
        quiz = json.loads(content)
    except json.JSONDecodeError as exc:
        # Recover if the model adds text around the JSON.
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise RuntimeError(
                "Ollama returned invalid quiz JSON. Please try again."
            ) from exc
        try:
            quiz = json.loads(match.group(0))
        except json.JSONDecodeError as inner_exc:
            raise RuntimeError(
                "Could not parse the quiz returned by Ollama."
            ) from inner_exc

    questions = quiz.get("questions")

    if not isinstance(questions, list) or not questions:
        raise RuntimeError("Ollama did not return any quiz questions.")

    validated_questions = []

    for index, item in enumerate(questions[:num_questions]):
        if not isinstance(item, dict):
            continue

        question_text = item.get("question")
        options = item.get("options")
        correct_answer = item.get("correct_answer")

        if (
            not isinstance(question_text, str)
            or not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(option, str) for option in options)
            or not isinstance(correct_answer, int)
            or isinstance(correct_answer, bool)
            or not 0 <= correct_answer < 4
        ):
            continue

        validated_questions.append({
            "id": str(item.get("id", f"q{index + 1}")),
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": str(item.get("explanation", "")),
        })

    if len(validated_questions) != num_questions:
        raise RuntimeError(
            "Ollama returned an incomplete or invalid quiz. "
            "Please generate it again."
        )

    return {"questions": validated_questions}
