import re

with open('app/ml_engine.py', 'r') as f:
    content = f.read()

explain_func = """
def explain_customer(customer_id: str) -> dict:
    \"\"\"
    Dynamically generate full SHAP values for a single customer for a Waterfall chart.
    \"\"\"
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
"""

if "def explain_customer" not in content:
    content += explain_func
    with open('app/ml_engine.py', 'w') as f:
        f.write(content)
        print("Patched ml_engine.py")
else:
    print("Already patched")
