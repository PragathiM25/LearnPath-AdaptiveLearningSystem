
import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

def resolve_path(value: str, default: str) -> Path:
    path = Path(os.getenv(value, default))
    if not path.is_absolute():
        path = BACKEND_DIR / path
    return path.resolve()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

CHROMA_PATH = resolve_path("CHROMA_PATH", "chroma_db")
MODEL_PATH = resolve_path(
    "MODEL_PATH", "models/learnpath_student_model.joblib"
)
DATABASE_PATH = resolve_path("DATABASE_PATH", "learnpath.db")
UPLOAD_PATH = resolve_path("UPLOAD_PATH", "uploads")

for directory in [
    CHROMA_PATH,
    MODEL_PATH.parent,
    UPLOAD_PATH,
    DATABASE_PATH.parent,
]:
    directory.mkdir(parents=True, exist_ok=True)
