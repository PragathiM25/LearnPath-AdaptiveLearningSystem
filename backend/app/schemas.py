
from pydantic import BaseModel, Field


class TutorRequest(BaseModel):
    question: str = Field(min_length=2, max_length=3000)
    student_id: str = Field(default="demo-student", max_length=100)


class QuizRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=150)
    number_of_questions: int = Field(default=5, ge=1, le=10)
    difficulty: str = Field(default="medium")


class QuizAnswer(BaseModel):
    question_id: str
    selected_option: int = Field(ge=0, le=3)


class QuizSubmission(BaseModel):
    student_id: str = Field(default="demo-student", max_length=100)
    topic: str = Field(min_length=1, max_length=150)
    answers: list[QuizAnswer]
