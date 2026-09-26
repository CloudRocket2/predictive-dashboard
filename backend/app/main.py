"""
FastAPI Application Entrypoint.

On startup:
1. Creates all database tables in Neon PostgreSQL.
2. Seeds the database with the Telco Churn dataset (if empty).
3. Trains the ML model and saves predictions.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import async_engine, Base
from app.models import Customer, Prediction, ModelMetadata  # noqa: ensure models registered
from app.ml_engine import seed_database, train_and_predict
from app.routers import dashboard

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, seed data, train model."""
    logger.info("🚀 Starting up Predictive Churn API...")

    # Create tables (async engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables ready.")

    # Seed data (sync — downloads CSV and bulk inserts)
    seed_database()
    logger.info("✅ Database seeded.")

    # Train model on first startup
    try:
        metrics = train_and_predict()
        logger.info(f"✅ Model trained. ROC-AUC: {metrics['roc_auc']}")
    except Exception as e:
        logger.error(f"❌ Initial training failed: {e}")

    yield

    # Shutdown
    await async_engine.dispose()
    logger.info("👋 Shutting down.")


app = FastAPI(
    title="Predictive Churn Dashboard API",
    description="Enterprise-grade churn prediction with XGBoost, SHAP explainability, and drift monitoring.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend (local dev + Vercel deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "Predictive Churn API"}
