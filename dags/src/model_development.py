# File: src/model_development.py
"""
Model development module for Airflow ML pipeline.

This module provides data loading, preprocessing, model training, evaluation,
and persistence utilities for the Airflow pipeline.

It uses relative paths and Airflow-friendly logging.
"""

import os
import pickle
import logging
from typing import Dict

import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
WORKING_DIR = os.path.join(BASE_DIR, "working_data")
MODEL_DIR = os.path.join(BASE_DIR, "model")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(WORKING_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# === Logger ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data() -> str:
    """Load dataset and save as pickle."""
    csv_path = os.path.join(DATA_DIR, "advertising.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    out_path = os.path.join(WORKING_DIR, "raw.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(df, f)

    logger.info("✅ Data loaded and saved to: %s", out_path)
    return out_path


def data_preprocessing(file_path: str) -> str:
    """Preprocess data: split, scale, and save."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pickle file not found: {file_path}")

    with open(file_path, "rb") as f:
        df = pickle.load(f)

    X = df.drop(["Timestamp", "Clicked on Ad", "Ad Topic Line", "Country", "City"], axis=1)
    y = df["Clicked on Ad"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    num_columns = ["Daily Time Spent on Site", "Age", "Area Income", "Daily Internet Usage", "Male"]
    scaler = StandardScaler()
    column_transformer = make_column_transformer((scaler, num_columns), remainder="passthrough")

    X_train_tr = column_transformer.fit_transform(X_train)
    X_test_tr = column_transformer.transform(X_test)

    out_path = os.path.join(WORKING_DIR, "preprocessed.pkl")
    with open(out_path, "wb") as f:
        pickle.dump((X_train_tr, X_test_tr, y_train.values, y_test.values), f)

    logger.info("✅ Preprocessing complete. Data saved to: %s", out_path)
    return out_path


def separate_data_outputs(file_path: str) -> str:
    """Passthrough function to preserve DAG task structure."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info("ℹ️ Data path passed through: %s", file_path)
    return file_path


def build_model(file_path: str, filename: str) -> str:
    """Train logistic regression model and save it."""
    with open(file_path, "rb") as f:
        X_train, X_test, y_train, y_test = pickle.load(f)

    model = LogisticRegression(max_iter=500)
    model.fit(X_train, y_train)

    model_path = os.path.join(MODEL_DIR, filename)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    logger.info("✅ Model trained and saved to: %s", model_path)
    return model_path


def load_model(file_path: str, filename: str) -> Dict[str, float]:
    """Load model and evaluate on test set."""
    with open(file_path, "rb") as f:
        _, X_test, _, y_test = pickle.load(f)

    model_path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
    }

    logger.info("📈 Model evaluation metrics: %s", metrics)
    return metrics


def evaluate_model(file_path: str, filename: str) -> Dict[str, float]:
    """Wrapper to evaluate model explicitly (kept for DAG readability)."""
    return load_model(file_path, filename)
