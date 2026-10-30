
from collections import defaultdict

from .database import get_attempts
from .ml_model import predict_next_success


def build_student_features(attempts, topic):
    selected = [
        row for row in attempts
        if row["topic"].strip().lower() == topic.strip().lower()
    ]

    all_prior = attempts
    skill_correct = [row["correct"] for row in selected]

    def rate(rows):
        if not rows:
            return None
        return sum(int(row["correct"]) for row in rows) / len(rows)

    return {
        "history_count": len(all_prior),
        "prior_accuracy": rate(all_prior),
        "prior_hint_rate": 0.0,
        "prior_saw_answer_rate": 0.0,
        "prior_skill_attempts": len(selected),
        "prior_skill_accuracy": rate(selected),
        # This demo records topic names rather than source skill IDs.
        "problem_type": "multiple_choice",
        "answer_type": "multiple_choice",
        "skill_id": topic,
    }


def get_performance(student_id: str):
    attempts = get_attempts(student_id)
    topics = defaultdict(list)

    for row in attempts:
        topics[row["topic"]].append(int(row["correct"]))

    results = []
    for topic, scores in topics.items():
        accuracy = sum(scores) / len(scores)
        if len(scores) < 3:
            label = "Collecting evidence"
        elif accuracy < 0.4:
            label = "Needs revision"
        elif accuracy < 0.7:
            label = "Developing"
        elif accuracy < 0.85:
            label = "Good progress"
        else:
            label = "Strong performance"

        results.append({
            "topic": topic,
            "attempts": len(scores),
            "correct": sum(scores),
            "accuracy": round(accuracy, 3),
            "status": label,
        })

    return sorted(results, key=lambda item: item["accuracy"])


def get_learning_path(student_id: str):
    attempts = get_attempts(student_id)
    performance = get_performance(student_id)

    recommendations = []
    for item in performance:
        features = build_student_features(attempts, item["topic"])
        prediction = predict_next_success(features)

        recommendations.append({
            **item,
            "prediction": prediction,
            "recommendation": (
                "Review the fundamentals and practise an example."
                if item["accuracy"] < 0.4
                else "Practise more questions on this topic."
                if item["accuracy"] < 0.7
                else "Try a harder question to strengthen understanding."
            ),
        })

    return {
        "student_id": student_id,
        "topics": recommendations,
        "message": (
            "Complete a few quizzes to build a useful learning path."
            if not attempts
            else "Recommendations are based on recorded quiz attempts."
        ),
    }
