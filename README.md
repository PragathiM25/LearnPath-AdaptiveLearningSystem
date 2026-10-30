# LearnPath – Adaptive Learning and Knowledge Gap Assistant

<p align="center">

**An AI-powered platform for personalized, adaptive, and intelligent learning.**

</p>

## Overview

LearnPath is an AI-powered adaptive learning platform designed to improve the learning experience through personalized assistance, intelligent assessments, and student performance analysis.

The platform helps learners understand concepts, identify knowledge gaps, practice topic-based quizzes, and receive personalized learning recommendations.

It combines **Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and Machine Learning (ML)** to create an interactive learning environment.

LearnPath uses locally hosted AI through Ollama, allowing AI-powered features to run without depending on a paid external LLM API.

## Key Features

### 1. AI-Powered Learning Assistant
- Provides explanations for academic and technical questions.
- Answers learner queries using an integrated local LLM.
- Supports context-aware learning assistance.

### 2. PDF-Based Learning and RAG
- Allows users to upload learning materials in PDF format.
- Extracts text from uploaded documents.
- Converts document content into embeddings.
- Stores and retrieves relevant information using a vector database.
- Generates answers grounded in uploaded study materials.

### 3. Intelligent Quiz Generation
- Generates quizzes based on selected topics.
- Supports different difficulty levels.
- Creates questions using relevant learning content.
- Helps students evaluate their understanding.

### 4. Quiz Evaluation and Performance Analysis
- Evaluates submitted quiz answers.
- Calculates student scores.
- Analyzes topic-wise performance.
- Identifies areas requiring additional practice.

### 5. Knowledge Gap Detection
- Identifies weak topics based on quiz performance.
- Highlights concepts that require improvement.
- Helps learners understand their knowledge gaps.

### 6. Machine Learning-Based Performance Prediction
- Uses a trained ML model to analyze student-related features.
- Predicts student performance based on the model's input features.
- Supports data-driven learning analysis.

### 7. Personalized Learning Recommendations
- Helps learners focus on weaker topics.
- Encourages targeted revision and practice.
- Supports a more structured learning journey.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| AI / LLM | Ollama, Llama 3.2 (3B) |
| RAG | Retrieval-Augmented Generation |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Model Serialization | Joblib |
| API Testing | Swagger UI |
| Development Environment | Visual Studio Code |

## System Architecture

The application follows a frontend–backend architecture.

1. **Frontend:** Provides the user interface for uploading PDFs, asking questions, generating quizzes, and viewing learning results.
2. **Backend:** Uses FastAPI to handle API requests, document processing, quiz operations, and ML predictions.
3. **Document Processing:** Extracts text from PDFs and prepares content for retrieval.
4. **RAG Pipeline:** Retrieves relevant document sections to provide context to the AI assistant.
5. **LLM Integration:** Ollama runs the Llama 3.2 (3B) model locally to generate responses.
6. **ML Module:** Uses the trained Scikit-learn model to support student-performance prediction.
7. **Data Analysis:** Pandas and NumPy support data preparation and analysis.

## Project Structure

```text
LearnPath/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── llm.py
│   │   ├── ml_model.py
│   │   └── ...
│   │
│   ├── ml/
│   │   └── train_model.py
│   │
│   ├── models/
│   │   └── learnpath_student_model.joblib
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

*Note: The structure above represents the main project components. Actual filenames and folders may vary depending on your implementation.*

## Installation and Setup

### Prerequisites

Install the following before running the application:

- Python 3.12
- Node.js and npm
- Git
- Ollama

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/LearnPath-Adaptive-Learning-System.git
cd LearnPath-Adaptive-Learning-System
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Ollama

Install Ollama and download the required model:

```bash
ollama pull llama3.2:3b
```

Make sure the Ollama service is running.

Verify the installed model:

```bash
ollama list
```

### 4. Start the Backend

From the backend directory, run:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Frontend Setup

Open a second terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Open the local development URL displayed in the terminal, usually:

```text
http://localhost:5173
```

## Machine Learning Module

LearnPath integrates a machine learning module for student-performance analysis.

The model workflow includes:

1. Dataset preparation.
2. Data preprocessing.
3. Feature preparation and selection, where implemented.
4. Training the selected ML estimator.
5. Evaluating model performance.
6. Saving the trained model using Joblib.
7. Loading the saved model for prediction.

### Evaluation Metrics

The model can be evaluated using:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion Matrix

*The exact estimator, target variable, dataset, train-test split, and achieved metric values should be documented from the actual training implementation and evaluation output.*

## API Endpoints

The backend exposes API endpoints through FastAPI.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/tutor/ask` | POST | Ask the AI learning assistant a question |
| `/api/quiz/generate` | POST | Generate a topic-based quiz |

Additional document upload, retrieval, evaluation, and analytics endpoints depend on the backend implementation.

Explore the available API endpoints through Swagger:

`http://127.0.0.1:8000/docs`

## Advantages

- Personalized learning support.
- AI-powered academic assistance.
- Learning from uploaded study materials.
- Automated quiz generation.
- Identification of weak topics.
- Data-driven student-performance analysis.
- Local LLM integration.
- Reduced dependency on external AI APIs.

## Future Enhancements

- Student progress tracking and learning history.
- Advanced personalized learning paths.
- More comprehensive performance analytics.
- Support for additional document formats.
- Multilingual learning assistance.
- Improved recommendation algorithms.
- Enhanced model evaluation and validation.
- Deployment for multiple users.

## Project Objective

The primary objective of LearnPath is to make learning more personalized, accessible, and effective by combining AI-powered assistance, document-based knowledge retrieval, automated assessment, and machine learning.

Instead of following the same learning path for every student, LearnPath aims to help each learner understand their strengths, identify weaknesses, and focus on areas that need improvement.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**LearnPath – Learn Smarter. Identify Gaps. Grow Better.**
