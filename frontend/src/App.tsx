
import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LoaderCircle,
  MessageCircle,
  Send,
  Sparkles,
  Target,
  Upload,
  XCircle,
} from "lucide-react";

import {
  askTutor,
  generateQuiz,
  getDocuments,
  getHealth,
  getLearningPath,
  getStudentSummary,
  submitQuiz,
  uploadDocument,
  type DocumentInfo,
  type QuizSession,
  type QuizResult,
} from "./api";

type Tab = "overview" | "tutor" | "quiz" | "materials" | "path";

const STUDENT_ID = "demo-student";

export default function App() {
  const [tab, setTab] = useState<Tab>("overview");
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [path, setPath] = useState<Awaited<ReturnType<typeof getLearningPath>> | null>(null);
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof getStudentSummary>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");

  const [question, setQuestion] = useState("");
  const [tutorAnswer, setTutorAnswer] = useState("");
  const [tutorSources, setTutorSources] = useState<{ document: string; page: number }[]>([]);

  const [topic, setTopic] = useState("Introduction to Machine Learning");
  const [difficulty, setDifficulty] = useState("medium");
  const [quiz, setQuiz] = useState<QuizSession | null>(null);
  const [selected, setSelected] = useState<Record<string, number>>({});
  const [result, setResult] = useState<QuizResult | null>(null);

  async function refreshDashboard() {
    let backendReachable = false;
    try {
      await getHealth();
      backendReachable = true;
      setApiStatus("online");
      const [docs, learningPath, studentSummary] = await Promise.all([
        getDocuments(),
        getLearningPath(STUDENT_ID),
        getStudentSummary(STUDENT_ID),
      ]);
      setDocuments(docs.documents);
      setPath(learningPath);
      setSummary(studentSummary);
      setError("");
    } catch (e) {
      setApiStatus(backendReachable ? "online" : "offline");
      setError(e instanceof Error ? e.message : "Could not load data from the backend.");
    }
  }

  useEffect(() => {
    void refreshDashboard();
  }, []);

  async function handleUpload(file?: File) {
    if (!file) return;
    setBusy(true);
    setError("");
    setNotice("");

    try {
      const response = await uploadDocument(file);
      setNotice(`${response.filename} indexed successfully.`);
      await refreshDashboard();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleAsk() {
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    setTutorAnswer("");
    setTutorSources([]);

    try {
      const response = await askTutor(question.trim());
      setTutorAnswer(response.answer);
      setTutorSources(response.sources);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Tutor request failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleGenerateQuiz() {
    setBusy(true);
    setError("");
    setResult(null);
    setSelected({});
    setQuiz(null);

    try {
      const response = await generateQuiz(topic, 5, difficulty);
      setQuiz(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Quiz generation failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmitQuiz() {
    if (!quiz) return;
    if (Object.keys(selected).length !== quiz.questions.length) {
      setError("Please answer every question before submitting.");
      return;
    }

    setBusy(true);
    setError("");

    try {
      const answers = quiz.questions.map((q) => ({
        question_id: q.question_id,
        selected_option: selected[q.question_id],
      }));

      const response = await submitQuiz(
        quiz.session_id,
        quiz.topic,
        answers,
        STUDENT_ID
      );

      setResult(response);
      setQuiz(null);
      await refreshDashboard();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Quiz submission failed.");
    } finally {
      setBusy(false);
    }
  }

  const navItems: { id: Tab; label: string; icon: typeof LayoutDashboard }[] = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "tutor", label: "AI Tutor", icon: MessageCircle },
    { id: "quiz", label: "Practice Quiz", icon: CircleHelp },
    { id: "materials", label: "Study Materials", icon: BookOpen },
    { id: "path", label: "Learning Path", icon: Target },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><BrainCircuit size={24} /></div>
          <div>
            <strong>LearnPath</strong>
            <span>YOUR AI STUDY SPACE</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav className="navigation">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${tab === id ? "active" : ""}`}
              onClick={() => { setTab(id); setError(""); setNotice(""); }}
            >
              <Icon size={18} />
              <span>{label}</span>
              {tab === id && <ChevronRight className="nav-chevron" size={16} />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="ai-status"><span className="status-dot" /> AI learning engine</div>
          <div className="profile">
            <div className="avatar">S</div>
            <div><strong>Student workspace</strong><span>Local demo profile</span></div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {navItems.find((n) => n.id === tab)?.label}</div>
          <div className="topbar-right">
            <span className={`online-dot ${apiStatus}`} />
            {apiStatus === "checking" ? "Connecting to backend…" : apiStatus === "online" ? "Backend connected" : "Backend unavailable"}
          </div>
        </header>

        <div className="page-content">
          {error && (
            <div className="alert error-alert">
              <XCircle size={18} /> <span>{error}</span>
              <button onClick={() => setError("")} aria-label="Dismiss error"><XCircle size={16} /></button>
            </div>
          )}
          {notice && <div className="alert success-alert"><CheckCircle2 size={18} />{notice}</div>}

          {tab === "overview" && (
            <>
              <section className="welcome-row">
                <div>
                  <div className="eyebrow"><Sparkles size={14} /> YOUR PERSONAL AI LEARNING ASSISTANT</div>
                  <h1>Make learning <span className="gradient-text">feel clearer.</span></h1>
                  <p>Your study space adapts as you practise, ask questions, and explore new topics.</p>
                </div>
                <div className="welcome-orb"><div className="orb-core"><BrainCircuit size={34} /></div></div>
              </section>

              <section className="stat-grid">
                <StatCard icon={<Target />} label="Questions attempted" value={summary?.total_attempts ?? 0} caption="Across your practice quizzes" />
                <StatCard icon={<CheckCircle2 />} label="Correct answers" value={summary?.correct_answers ?? 0} caption="Answers marked correct" />
                <StatCard icon={<Activity />} label="Overall accuracy" value={`${Math.round((summary?.accuracy ?? 0) * 100)}%`} caption="Based on recorded attempts" />
                <StatCard icon={<BookOpen />} label="Topics explored" value={summary?.topics ?? 0} caption="Topics with practice history" />
              </section>

              <section className="section-heading">
                <div><h2>Your learning workspace</h2><p>Choose what you want to work on next.</p></div>
              </section>
              <section className="feature-grid">
                <FeatureCard icon={<MessageCircle />} tag="ASK & EXPLORE" title="AI Tutor" description="Get clear explanations grounded in your uploaded notes." action="Ask a question" onClick={() => setTab("tutor")} />
                <FeatureCard icon={<CircleHelp />} tag="PRACTISE" title="Knowledge check" description="Try a short quiz and discover which concepts need revision." action="Start practice" onClick={() => setTab("quiz")} />
                <FeatureCard icon={<Target />} tag="YOUR NEXT STEP" title="Learning path" description="See topic-level performance and practical revision suggestions." action="View learning path" onClick={() => setTab("path")} />
              </section>

              <section className="panel recent-panel">
                <div className="panel-title-row"><div><h2>Recommended next steps</h2><p>Suggestions from your recorded practice</p></div><button className="text-button" onClick={() => setTab("path")}>View all <ArrowRight size={15} /></button></div>
                {path?.topics.length ? path.topics.slice(0, 3).map((item) => (
                  <div className="recommendation-row" key={item.topic}>
                    <div className="recommendation-icon"><BookOpen size={18} /></div>
                    <div className="recommendation-main"><strong>{item.topic}</strong><span>{item.recommendation}</span></div>
                    <span className={`status-pill ${item.accuracy < 0.4 ? "needs-work" : "in-progress"}`}>{item.status}</span>
                  </div>
                )) : <EmptyState text="Complete a practice quiz to see personalised topic recommendations here." />}
              </section>
            </>
          )}

          {tab === "materials" && (
            <PageHeading eyebrow="YOUR KNOWLEDGE BASE" title="Study materials" description="Upload text-based PDFs so your AI tutor can search your notes." />
          )}
          {tab === "materials" && (
            <>
              <label className="upload-zone">
                <input type="file" accept="application/pdf,.pdf" onChange={(e) => { void handleUpload(e.target.files?.[0]); e.currentTarget.value = ""; }} />
                <div className="upload-icon"><Upload size={25} /></div>
                <h3>{busy ? "Processing your material…" : "Add a study PDF"}</h3>
                <p>Select a PDF up to 20 MB. Scanned PDFs may need OCR first.</p>
                <span className="button-look"><Upload size={16} /> Choose PDF</span>
              </label>
              <section className="panel">
                <div className="panel-title-row"><div><h2>Uploaded documents</h2><p>{documents.length} documents available to your tutor</p></div><FileText size={20} /></div>
                {documents.length ? documents.map((doc) => (
                  <div className="document-row" key={doc.id}><FileText size={19} /><div><strong>{doc.filename}</strong><span>Uploaded {doc.uploaded_at}</span></div><CheckCircle2 className="success-icon" size={18} /></div>
                )) : <EmptyState text="Your uploaded PDFs will appear here." />}
              </section>
            </>
          )}

          {tab === "tutor" && (
            <>
              <PageHeading eyebrow="LEARN THROUGH CONVERSATION" title="Your AI tutor" description="Ask a question, untangle a concept, or request a step-by-step explanation." />
              <section className="panel tutor-panel">
                <div className="tutor-intro"><div className="assistant-avatar"><Sparkles size={23} /></div><div><strong>LearnPath assistant</strong><span>Here to help you understand, not just memorise.</span></div></div>
                <label className="field-label" htmlFor="tutor-question">What would you like to understand?</label>
                <textarea id="tutor-question" rows={4} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="For example: Explain overfitting in machine learning with a simple example…" />
                <div className="composer-footer"><span>Answers use uploaded notes when relevant.</span><button className="primary-button" disabled={busy || !question.trim()} onClick={() => void handleAsk()}>{busy ? <LoaderCircle className="spin" size={17} /> : <Send size={16} />} Ask tutor</button></div>
                {tutorAnswer && <div className="answer-box"><div className="answer-heading"><Sparkles size={17} /> Explanation</div><p className="answer-text">{tutorAnswer}</p>{tutorSources.length > 0 && <div className="source-list"><strong>Retrieved sources</strong>{tutorSources.map((s, i) => <span key={`${s.document}-${s.page}-${i}`}>{s.document}, page {s.page}</span>)}</div>}</div>}
              </section>
            </>
          )}

          {tab === "quiz" && (
            <>
              <PageHeading eyebrow="BUILD CONFIDENCE THROUGH PRACTICE" title="Practice quiz" description="Generate a small set of questions, submit your answers, and learn from the explanations." />
              <section className="panel quiz-panel">
                {!quiz && !result && (
                  <div className="quiz-setup">
                    <div className="quiz-art"><GraduationCap size={35} /><span>5 QUESTIONS · QUICK PRACTICE</span></div>
                    <label className="field-label" htmlFor="topic">Topic</label>
                    <input id="topic" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Enter a subject or topic" />
                    <label className="field-label" htmlFor="difficulty">Difficulty</label>
                    <select id="difficulty" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select>
                    <button className="primary-button full-button" disabled={busy || !topic.trim()} onClick={() => void handleGenerateQuiz()}>{busy ? <LoaderCircle className="spin" size={17} /> : <Sparkles size={17} />} Generate my quiz</button>
                  </div>
                )}

                {quiz && (
                  <div className="question-list">
                    <div className="quiz-progress-heading"><div><span className="eyebrow">YOUR PRACTICE SESSION</span><h2>{quiz.topic}</h2></div><span>{Object.keys(selected).length}/{quiz.questions.length} answered</span></div>
                    <div className="progress-track"><div className="progress-fill" style={{ width: `${Object.keys(selected).length / quiz.questions.length * 100}%` }} /></div>
                    {quiz.questions.map((q, i) => (
                      <div className="question-card" key={q.question_id}>
                        <div className="question-number">QUESTION {i + 1}</div><h3>{q.question}</h3>
                        <div className="option-list">{q.options.map((option, optionIndex) => (
                          <button key={optionIndex} className={`option-button ${selected[q.question_id] === optionIndex ? "selected" : ""}`} onClick={() => setSelected((old) => ({ ...old, [q.question_id]: optionIndex }))}>
                            <span className="option-letter">{String.fromCharCode(65 + optionIndex)}</span>{option}
                          </button>
                        ))}</div>
                      </div>
                    ))}
                    <button className="primary-button full-button" disabled={busy} onClick={() => void handleSubmitQuiz()}>{busy ? <LoaderCircle className="spin" size={17} /> : <CheckCircle2 size={17} />} Submit answers</button>
                  </div>
                )}

                {result && (
                  <div className="result-view">
                    <div className="result-orb"><CheckCircle2 size={32} /></div>
                    <div className="eyebrow">PRACTICE COMPLETE</div>
                    <h2>{result.score} / {result.total} correct</h2>
                    <p>{result.message}</p>
                    <div className="result-progress"><div className="progress-track"><div className="progress-fill" style={{ width: `${result.accuracy * 100}%` }} /></div><strong>{Math.round(result.accuracy * 100)}% accuracy</strong></div>
                    <div className="feedback-list">{result.feedback.map((item, i) => <div className="feedback-row" key={item.question_id}>{item.correct ? <CheckCircle2 className="success-icon" /> : <XCircle className="error-icon" />}<div><strong>Question {i + 1}: {item.correct ? "Correct" : `Correct option: ${String.fromCharCode(65 + item.correct_option)}`}</strong><span>{item.explanation}</span></div></div>)}</div>
                    <button className="primary-button full-button" onClick={() => { setResult(null); setQuiz(null); setSelected({}); }}>Practise another topic</button>
                  </div>
                )}
              </section>
            </>
          )}

          {tab === "path" && (
            <>
              <PageHeading eyebrow="SMALL STEPS, REAL PROGRESS" title="Your learning path" description="Use your quiz history to decide what to revise next." />
              <section className="panel">
                <div className="panel-title-row"><div><h2>Topic performance</h2><p>{path?.message ?? "Loading your learning data…"}</p></div><Target size={21} /></div>
                {path?.topics.length ? path.topics.map((item) => (
                  <div className="path-card" key={item.topic}>
                    <div className="path-card-header"><div><h3>{item.topic}</h3><span>{item.attempts} attempts · {item.correct} correct</span></div><span className={`status-pill ${item.accuracy < 0.4 ? "needs-work" : "in-progress"}`}>{item.status}</span></div>
                    <div className="path-progress"><div className="progress-track"><div className="progress-fill" style={{ width: `${item.accuracy * 100}%` }} /></div><span>{Math.round(item.accuracy * 100)}%</span></div>
                    <p>{item.recommendation}</p>
                    {item.prediction?.available && <div className="prediction-note"><BrainCircuit size={16} /><span>Model estimate: {Math.round((item.prediction.predicted_success_probability ?? 0) * 100)}% likelihood of success on a similar question. {item.prediction.guidance}</span></div>}
                    {!item.prediction?.available && <div className="prediction-note"><Activity size={16} /><span>Rule-based recommendation shown. The trained model prediction is currently unavailable.</span></div>}
                  </div>
                )) : <EmptyState text="Complete your first practice quiz to start building a topic-level learning path." />}
              </section>
            </>
          )}
          <footer className="footer-note"><Sparkles size={14} /> LearnPath · Your progress, one concept at a time.</footer>
        </div>
      </main>
    </div>
  );
}

function PageHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <section className="page-heading"><div className="eyebrow"><Sparkles size={14} /> {eyebrow}</div><h1>{title}</h1><p>{description}</p></section>;
}

function StatCard({ icon, label, value, caption }: { icon: React.ReactNode; label: string; value: string | number; caption: string }) {
  return <div className="stat-card"><div className="stat-top"><span className="stat-icon">{icon}</span><span className="stat-live">LIVE</span></div><div className="stat-value">{value}</div><div className="stat-label">{label}</div><div className="stat-caption">{caption}</div></div>;
}

function FeatureCard({ icon, tag, title, description, action, onClick }: { icon: React.ReactNode; tag: string; title: string; description: string; action: string; onClick: () => void }) {
  return <button className="feature-card" onClick={onClick}><div className="feature-icon">{icon}</div><div className="feature-tag">{tag}</div><h3>{title}</h3><p>{description}</p><span className="feature-action">{action}<ArrowRight size={16} /></span></button>;
}

function EmptyState({ text }: { text: string }) {
  return <div className="empty-state"><div className="empty-icon"><BookOpen size={22} /></div><p>{text}</p></div>;
}
