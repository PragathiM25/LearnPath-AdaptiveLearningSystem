
from functools import lru_cache
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from .config import CHROMA_PATH, EMBEDDING_MODEL

COLLECTION_NAME = "learnpath_materials"


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def split_text(text: str, chunk_size: int = 900, overlap: int = 150):
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap

    return chunks


def index_pages(document_name: str, pages: list[str]):
    collection = get_collection()
    model = get_embedding_model()

    ids, texts, metadatas = [], [], []

    for page_number, page_text in enumerate(pages, start=1):
        for chunk_number, chunk in enumerate(split_text(page_text)):
            digest = hashlib.sha256(
                f"{document_name}:{page_number}:{chunk_number}".encode()
            ).hexdigest()[:24]

            ids.append(digest)
            texts.append(chunk)
            metadatas.append({
                "document": document_name,
                "page": page_number,
                "chunk": chunk_number,
            })

    if not texts:
        return 0

    embeddings = model.encode(
        texts, normalize_embeddings=True
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return len(texts)


def retrieve(question: str, n_results: int = 4):
    collection = get_collection()

    if collection.count() == 0:
        return []

    model = get_embedding_model()
    embedding = model.encode(
        [question], normalize_embeddings=True
    ).tolist()

    result = collection.query(
        query_embeddings=embedding,
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    passages = []
    for i, document in enumerate(result["documents"][0]):
        passages.append({
            "text": document,
            "metadata": result["metadatas"][0][i],
            "distance": result["distances"][0][i],
        })

    return passages
