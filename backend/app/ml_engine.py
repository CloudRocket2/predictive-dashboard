"""
ML Engine: Handles training, prediction, explainability, and drift detection.

This module encapsulates the entire ML lifecycle:
1. Data loading & leakage-proof splitting
2. XGBoost training via sklearn Pipeline
3. Bootstrapped prediction intervals
4. SHAP-based explainability (top 3 drivers)
5. PSI drift monitoring
6. Persistence of predictions to PostgreSQL
"""

import logging
import numpy as np
import pandas as pd
import shap
import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss
from sqlalchemy import text

from app.database import sync_engine, SyncSessionLocal
from app.models import Base, Customer, Prediction, ModelMetadata

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "model_artifacts"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "churn_pipeline.joblib"

# Columns to drop from the feature set to prevent data leakage
DROP_COLS = ["customerID", "Churn", "Actual_Churn", "TotalCharges"]

# Number of bootstrap iterations for prediction intervals
N_BOOTSTRAP = 50


def _download_dataset() -> pd.DataFrame:
    """Download the IBM Telco Customer Churn dataset."""
    url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
    df = pd.read_csv(url)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace(" ", np.nan)).fillna(0)
    df["Actual_Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
    return df


def seed_database():
    """Download dataset and seed the customers table in PostgreSQL."""
    logger.info("Seeding database with Telco Churn dataset...")
    Base.metadata.create_all(bind=sync_engine)

    # Check if already seeded
    with sync_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        if count > 0:
            logger.info(f"Database already seeded with {count} customers. Skipping.")
            return

    df = _download_dataset()

    # Normalize column names for the ORM
    col_map = {
        "customerID": "customer_id",
        "gender": "gender",
        "SeniorCitizen": "senior_citizen",
        "Partner": "partner",
        "Dependents": "dependents",
        "tenure": "tenure",
        "PhoneService": "phone_service",
        "MultipleLines": "multiple_lines",
        "InternetService": "internet_service",
        "OnlineSecurity": "online_security",
        "OnlineBackup": "online_backup",
        "DeviceProtection": "device_protection",
        "TechSupport": "tech_support",
        "StreamingTV": "streaming_tv",
        "StreamingMovies": "streaming_movies",
        "Contract": "contract",
        "PaperlessBilling": "paperless_billing",
        "PaymentMethod": "payment_method",
        "MonthlyCharges": "monthly_charges",
        "TotalCharges": "total_charges",
        "Churn": "churn",
    }
    db_df = df.rename(columns=col_map)[list(col_map.values())]
    db_df.to_sql("customers", sync_engine, if_exists="append", index=False)
    logger.info(f"Seeded {len(db_df)} customers into the database.")


def _load_data_from_db() -> pd.DataFrame:
    """Load all customer data from PostgreSQL back into a DataFrame."""
    df = pd.read_sql("SELECT * FROM customers", sync_engine)

    # Reverse column mapping to match the original dataset format the pipeline expects
    reverse_map = {
        "customer_id": "customerID",
        "senior_citizen": "SeniorCitizen",
        "partner": "Partner",
        "dependents": "Dependents",
        "phone_service": "PhoneService",
        "multiple_lines": "MultipleLines",
        "internet_service": "InternetService",
        "online_security": "OnlineSecurity",
        "online_backup": "OnlineBackup",
        "device_protection": "DeviceProtection",
        "tech_support": "TechSupport",
        "streaming_tv": "StreamingTV",
        "streaming_movies": "StreamingMovies",
        "contract": "Contract",
        "paperless_billing": "PaperlessBilling",
        "payment_method": "PaymentMethod",
        "monthly_charges": "MonthlyCharges",
        "total_charges": "TotalCharges",
        "churn": "Churn",
    }
    df = df.rename(columns=reverse_map)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    df["Actual_Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
    return df


def _temporal_split(df: pd.DataFrame):
    """
    Leakage-proof temporal split using tenure as a proxy for time.
    Train on customers with tenure <= 24 months, test on > 24.
    """
    train_df = df[df["tenure"] <= 24].copy()
    test_df = df[df["tenure"] > 24].copy()

    X_train = train_df.drop(columns=DROP_COLS)
    y_train = train_df["Actual_Churn"]
    X_test = test_df.drop(columns=DROP_COLS)
    y_test = test_df["Actual_Churn"]

    return X_train, y_train, X_test, y_test, train_df, test_df


def _build_pipeline(X_train: pd.DataFrame) -> Pipeline:
    """Build a sklearn pipeline with preprocessing and XGBoost classifier."""
    categorical_cols = X_train.select_dtypes(include=["object"]).columns.tolist()
    numeric_cols = X_train.select_dtypes(include=["number"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", XGBClassifier(
                random_state=42,
                eval_metric="logloss",
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                use_label_encoder=False,
            )),
        ]
    )
    return pipeline


def _bootstrap_intervals(
    pipeline: Pipeline, X_train: pd.DataFrame, y_train: pd.Series, X_test_transformed: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate prediction intervals via bootstrapping.
    Returns (lower_bound_10th_pct, upper_bound_90th_pct) arrays.
    """
    n_test = X_test_transformed.shape[0]
    bootstrap_preds = np.zeros((n_test, N_BOOTSTRAP))

    preprocessor = pipeline.named_steps["preprocessor"]

    for i in range(N_BOOTSTRAP):
        indices = np.random.choice(len(X_train), len(X_train), replace=True)
        X_boot = X_train.iloc[indices]
        y_boot = y_train.iloc[indices]

        X_boot_trans = preprocessor.transform(X_boot)
        boot_clf = XGBClassifier(
            random_state=i, eval_metric="logloss", n_estimators=200,
            max_depth=5, learning_rate=0.1, use_label_encoder=False, n_jobs=-1
        )
        boot_clf.fit(X_boot_trans, y_boot)
        bootstrap_preds[:, i] = boot_clf.predict_proba(X_test_transformed)[:, 1]

    lower = np.percentile(bootstrap_preds, 10, axis=1)
    upper = np.percentile(bootstrap_preds, 90, axis=1)
    return lower, upper


def _compute_shap_drivers(
    xgb_model: XGBClassifier, X_test_transformed: np.ndarray, feature_names: list[str]
) -> list[list[str]]:
    """Compute SHAP values and extract top 3 drivers per customer."""
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(X_test_transformed)

    all_drivers = []
    for i in range(len(shap_values)):
        impacts = pd.Series(shap_values[i], index=feature_names)
        top_3 = impacts.abs().sort_values(ascending=False).head(3).index.tolist()
        # Clean encoded names: 'cat__Contract_Month-to-month' -> 'Contract: Month-to-month'
        cleaned = []
        for name in top_3:
            clean = name.split("__")[-1]
            # Replace first underscore with ': ' for readability
            if "_" in clean:
                parts = clean.split("_", 1)
                clean = f"{parts[0]}: {parts[1]}"
            cleaned.append(clean)
        all_drivers.append(cleaned)

    return all_drivers


def calculate_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """
    Calculate Population Stability Index (PSI) between two distributions.
    PSI < 0.1: No significant shift
    PSI 0.1-0.25: Moderate shift
    PSI > 0.25: Significant shift — retrain recommended
    """
    breakpoints = np.linspace(
        min(expected.min(), actual.min()),
        max(expected.max(), actual.max()),
        bins + 1,
    )
    expected_pct = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_pct = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # Avoid log(0)
    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)

    psi = np.sum((expected_pct - actual_pct) * np.log(expected_pct / actual_pct))
    return float(psi)


def train_and_predict() -> dict:
    """
    Full ML lifecycle:
    1. Load data from Postgres
    2. Temporal split
    3. Train XGBoost pipeline
    4. Bootstrap intervals
    5. SHAP drivers
    6. PSI drift
    7. Save predictions + metadata to Postgres
    8. Persist model artifact to disk

    Returns a dict with training metrics.
    """
    logger.info("Starting model training pipeline...")

    np.random.seed(42)

    # Step 1: Load
    df = _load_data_from_db()

    # Step 2: Split
    X_train, y_train, X_test, y_test, train_df, test_df = _temporal_split(df)
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Step 3: Build & train
    pipeline = _build_pipeline(X_train)
    pipeline.fit(X_train, y_train)

    # Log feature importances to check for data leakage
    xgb_model = pipeline.named_steps["classifier"]
    feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    importances = xgb_model.feature_importances_
    
    # Sort and log top 10
    top_indices = np.argsort(importances)[::-1][:10]
    logger.info("Top 10 Feature Importances (Data Leakage Check):")
    for idx in top_indices:
        logger.info(f" - {feature_names[idx]}: {importances[idx]:.4f}")

    # Step 4: Predict
    probs = pipeline.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, probs)
    brier = brier_score_loss(y_test, probs)
    logger.info(f"ROC-AUC: {roc_auc:.4f} | Brier: {brier:.4f}")

    # Step 5: Bootstrap intervals
    X_test_transformed = pipeline.named_steps["preprocessor"].transform(X_test)
    lower, upper = _bootstrap_intervals(pipeline, X_train, y_train, X_test_transformed)

    # Step 6: SHAP
    feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out().tolist()
    xgb_model = pipeline.named_steps["classifier"]
    drivers = _compute_shap_drivers(xgb_model, X_test_transformed, feature_names)

    # Step 7: PSI
    psi = calculate_psi(
        train_df["MonthlyCharges"].values,
        test_df["MonthlyCharges"].values,
    )
    logger.info(f"MonthlyCharges PSI: {psi:.4f}")

    # Step 8: Save predictions to DB
    predictions_data = []
    for idx, (i, row) in enumerate(test_df.iterrows()):
        d = drivers[idx] if idx < len(drivers) else ["N/A", "N/A", "N/A"]
        predictions_data.append({
            "customer_id": row["customerID"],
            "monthly_charges": row["MonthlyCharges"],
            "actual_churn": int(row["Actual_Churn"]),
            "churn_probability": float(probs[idx]),
            "lower_bound": float(lower[idx]),
            "upper_bound": float(upper[idx]),
            "top_driver_1": d[0] if len(d) > 0 else "N/A",
            "top_driver_2": d[1] if len(d) > 1 else "N/A",
            "top_driver_3": d[2] if len(d) > 2 else "N/A",
            "dataset_split": "test",
        })

    pred_df = pd.DataFrame(predictions_data)

    # Clear old predictions and write new ones
    with sync_engine.begin() as conn:
        conn.execute(text("DELETE FROM predictions"))
        conn.execute(text("UPDATE model_metadata SET is_active = false"))
    pred_df.to_sql("predictions", sync_engine, if_exists="append", index=False)

    # Save model metadata
    meta = ModelMetadata(
        roc_auc=roc_auc,
        brier_score=brier,
        psi_monthly_charges=psi,
        train_size=len(X_train),
        test_size=len(X_test),
        is_active=True,
    )
    session = SyncSessionLocal()
    try:
        session.add(meta)
        session.commit()
    finally:
        session.close()

    # Save model to disk
    joblib.dump(pipeline, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")

    return {
        "roc_auc": round(roc_auc, 4),
        "brier_score": round(brier, 4),
        "psi_monthly_charges": round(psi, 4),
        "train_size": len(X_train),
        "test_size": len(X_test),
    }

def explain_customer(customer_id: str) -> dict:
    """
    Dynamically generate full SHAP values for a single customer for a Waterfall chart.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model artifact not found. Please train first.")
        
    pipeline = joblib.load(MODEL_PATH)
    
    # Load customer from DB
    df = pd.read_sql(f"SELECT * FROM customers WHERE customer_id = '{customer_id}'", sync_engine)
    if df.empty:
        raise ValueError("Customer not found")
        
    reverse_map = {
        "customer_id": "customerID", "senior_citizen": "SeniorCitizen",
        "partner": "Partner", "dependents": "Dependents", "phone_service": "PhoneService",
        "multiple_lines": "MultipleLines", "internet_service": "InternetService",
        "online_security": "OnlineSecurity", "online_backup": "OnlineBackup",
        "device_protection": "DeviceProtection", "tech_support": "TechSupport",
        "streaming_tv": "StreamingTV", "streaming_movies": "StreamingMovies",
        "contract": "Contract", "paperless_billing": "PaperlessBilling",
        "payment_method": "PaymentMethod", "monthly_charges": "MonthlyCharges",
        "total_charges": "TotalCharges", "churn": "Churn"
    }
    df = df.rename(columns=reverse_map)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    
    X = df.drop(columns=DROP_COLS, errors="ignore")
    
    preprocessor = pipeline.named_steps["preprocessor"]
    xgb_model = pipeline.named_steps["classifier"]
    
    X_trans = preprocessor.transform(X)
    
    # SHAP Explainer
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(X_trans)
    expected_value = explainer.expected_value
    
    if isinstance(expected_value, np.ndarray):
        expected_value = expected_value[0]
        
    feature_names = preprocessor.get_feature_names_out().tolist()
    
    # Clean feature names
    cleaned_names = []
    for name in feature_names:
        clean = name.split("__")[-1]
        if "_" in clean:
            parts = clean.split("_", 1)
            clean = f"{parts[0]}: {parts[1]}"
        cleaned_names.append(clean)
        
    # Zip values
    contributions = [{"feature": cleaned_names[i], "value": float(shap_values[0][i])} for i in range(len(cleaned_names))]
    
    # Sort by absolute magnitude to get most important
    contributions.sort(key=lambda x: abs(x["value"]), reverse=True)
    
    return {
        "base_value": float(expected_value),
        "contributions": contributions[:10] # Return top 10 for the chart
    }
