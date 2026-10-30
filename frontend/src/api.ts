
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map((item: { msg?: string }) => item.msg)
          .filter(Boolean)
          .join("; ") || message;
      }
    } catch {
      // Keep the fallback message if the response isn't JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export type DocumentInfo = {
  id: number;
  filename: string;
  uploaded_at: string;
};

export type QuizQuestion = {
  question_id: string;
  question: string;
  options: string[];
};

export type QuizSession = {
  session_id: string;
  topic: string;
  questions: QuizQuestion[];
  sources?: { document: string; page: number }[];
};

export type QuizResult = {
  score: number;
  total: number;
  accuracy: number;
  message: string;
  feedback: {
    question_id: string;
    correct: boolean;
    correct_option: number;
    explanation: string;
  }[];
};

export type TopicPerformance = {
  topic: string;
  attempts: number;
  correct: number;
  accuracy: number;
  status: string;
};

export async function getHealth() {
  return request<{ status: string }>("/health");
}

export async function getDocuments() {
  return request<{ documents: DocumentInfo[] }>("/documents");
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);

  return request<{
    id: number;
    filename: string;
    pages: number;
    indexed_chunks: number;
    message: string;
  }>("/documents/upload", {
    method: "POST",
    body: form,
  });
}

export async function askTutor(question: string) {
  return request<{
    answer: string;
    sources: { document: string; page: number }[];
    grounded_in_uploaded_material: boolean;
  }>("/tutor/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export async function generateQuiz(
  topic: string,
  number_of_questions = 5,
  difficulty = "medium"
) {
  return request<QuizSession>("/quiz/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic,
      number_of_questions,
      difficulty,
    }),
  });
}

export async function submitQuiz(
  sessionId: string,
  topic: string,
  answers: { question_id: string; selected_option: number }[],
  studentId = "demo-student"
) {
  return request<QuizResult>(
    `/quiz/submit?session_id=${encodeURIComponent(sessionId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, topic, answers }),
    }
  );
}

export async function getPerformance(studentId: string) {
  return request<{
    student_id: string;
    performance: TopicPerformance[];
  }>(`/performance/${encodeURIComponent(studentId)}`);
}

export async function getLearningPath(studentId: string) {
  return request<{
    student_id: string;
    topics: (TopicPerformance & {
      recommendation: string;
      prediction: {
        available: boolean;
        predicted_success_probability?: number;
        guidance?: string;
        message?: string;
      };
    })[];
    message: string;
  }>(`/learning-path/${encodeURIComponent(studentId)}`);
}

export async function getStudentSummary(studentId: string) {
  return request<{
    student_id: string;
    total_attempts: number;
    correct_answers: number;
    accuracy: number;
    topics: number;
  }>(`/student/${encodeURIComponent(studentId)}/summary`);
}
