"""
SQLAlchemy ORM models for the churn prediction database.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, func
from app.database import Base


class Customer(Base):
    """Raw customer data ingested from the Telco dataset."""
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    gender = Column(String)
    senior_citizen = Column(Integer)
    partner = Column(String)
    dependents = Column(String)
    tenure = Column(Integer)
    phone_service = Column(String)
    multiple_lines = Column(String)
    internet_service = Column(String)
    online_security = Column(String)
    online_backup = Column(String)
    device_protection = Column(String)
    tech_support = Column(String)
    streaming_tv = Column(String)
    streaming_movies = Column(String)
    contract = Column(String)
    paperless_billing = Column(String)
    payment_method = Column(String)
    monthly_charges = Column(Float)
    total_charges = Column(Float)
    churn = Column(String)  # 'Yes' / 'No'


class Prediction(Base):
    """Model predictions and explainability data for each customer."""
    __tablename__ = "predictions"

    customer_id = Column(String, primary_key=True, index=True)
    monthly_charges = Column(Float)
    actual_churn = Column(Integer)  # 0 or 1
    churn_probability = Column(Float)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    top_driver_1 = Column(String)
    top_driver_2 = Column(String)
    top_driver_3 = Column(String)
    dataset_split = Column(String)  # 'train' or 'test'


class ModelMetadata(Base):
    """Tracks model training runs and their performance metrics."""
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    roc_auc = Column(Float)
    brier_score = Column(Float)
    psi_monthly_charges = Column(Float)
    train_size = Column(Integer)
    test_size = Column(Integer)
    is_active = Column(Boolean, default=True)
