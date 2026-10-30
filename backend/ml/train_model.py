
from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
MODEL_DIR = BASE_DIR / "models"

def main():
    info_path = DATA_DIR / "studentInfo.csv"
    assessment_path = DATA_DIR / "studentAssessment.csv"
    assessments_path = DATA_DIR / "assessments.csv"

    for path in [info_path, assessment_path, assessments_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path.name}. Check backend/data/raw/"
            )

    students = pd.read_csv(info_path)
    scores = pd.read_csv(assessment_path)
    assessments = pd.read_csv(assessments_path)

    scores["score"] = pd.to_numeric(scores["score"], errors="coerce")
    assessments["weight"] = pd.to_numeric(
        assessments["weight"], errors="coerce"
    ).fillna(0)

    # Aggregate assessment scores available before the final outcome.
    merged = scores.merge(
        assessments[
            ["id_assessment", "code_module", "code_presentation",
             "date", "weight"]
        ],
        on="id_assessment",
        how="left",
        suffixes=("", "_assessment"),
    )

    # Keep only assessments associated with each student's course run.
    merged = merged[
        (merged["code_module"] == merged["code_module_assessment"])
        & (
            merged["code_presentation"]
            == merged["code_presentation_assessment"]
        )
    ] if "code_module_assessment" in merged.columns else merged

    # OULAD assessment scores are recorded before final course outcomes.
    merged["score"] = pd.to_numeric(merged["score"], errors="coerce")
    merged["weight"] = pd.to_numeric(merged["weight"], errors="coerce").fillna(0)
    merged["weighted_score"] = (
        merged["score"].fillna(0) * merged["weight"].fillna(0) / 100
    )

    aggregates = merged.groupby(
        ["id_student", "code_module", "code_presentation"]
    ).agg(
        mean_score=("score", "mean"),
        assessment_count=("score", "count"),
        weighted_score_total=("weighted_score", "sum"),
    ).reset_index()

    data = students.merge(
        aggregates,
        on=["id_student", "code_module", "code_presentation"],
        how="left",
    )

    data["assessment_count"] = data["assessment_count"].fillna(0)
    data["weighted_score_total"] = data["weighted_score_total"].fillna(0)

    # Drop outcomes without a usable final label.
    data = data[data["final_result"].isin(
        ["Pass", "Distinction", "Fail", "Withdrawn"]
    )].copy()

    if len(data) < 20:
        raise ValueError("Not enough labeled student records to train.")

    target = data["final_result"]

    # Exclude personal identifiers and post-outcome information.
    feature_columns = [
        "code_module",
        "code_presentation",
        "gender",
        "region",
        "highest_education",
        "imd_band",
        "age_band",
        "num_of_prev_attempts",
        "studied_credits",
        "disability",
        "mean_score",
        "assessment_count",
        "weighted_score_total",
    ]

    X = data[feature_columns].copy()
    y = target

    categorical = [
        "code_module", "code_presentation", "gender", "region",
        "highest_education", "imd_band", "age_band", "disability",
    ]
    numerical = [
        "num_of_prev_attempts", "studied_credits", "mean_score",
        "assessment_count", "weighted_score_total",
    ]

    preprocessor = ColumnTransformer([
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical),
        ("numerical", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numerical),
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=150,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": model,
        "feature_columns": feature_columns,
        "classes": list(model.classes_),
    }, MODEL_DIR / "learnpath_student_model.joblib")

    metrics = {
        "test_accuracy": accuracy_score(y_test, predictions),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "rows": len(data),
        "features": feature_columns,
        "target": "final_result",
    }

    with open(MODEL_DIR / "evaluation.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print(f"Test accuracy: {metrics['test_accuracy']:.3f}")
    print("Saved model to:", MODEL_DIR / "learnpath_student_model.joblib")
    print("Saved metrics to:", MODEL_DIR / "evaluation.json")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))

if __name__ == "__main__":
    main()
