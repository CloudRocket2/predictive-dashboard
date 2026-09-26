"""
API Router: Dashboard endpoints for KPIs, customers, simulation, and retraining.
"""

import logging
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel

from app.database import get_db
from app.models import Prediction, ModelMetadata
from app.ml_engine import train_and_predict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Dashboard"])


# ─── Pydantic Schemas ───────────────────────────────────────────────────────

class DriftMetrics(BaseModel):
    feature: str
    psi_score: float
    status: str  # "Stable", "Warning", "Critical"


class DashboardSummary(BaseModel):
    total_customers: int
    total_revenue: float
    revenue_at_risk: float
    avg_churn_risk: float
    model_roc_auc: float | None
    model_brier_score: float | None
    drift_metrics: DriftMetrics


class CustomerPrediction(BaseModel):
    customer_id: str
    monthly_charges: float
    actual_churn: int
    churn_probability: float
    lower_bound: float
    upper_bound: float
    top_drivers: list[str]


class CustomerListResponse(BaseModel):
    customers: list[CustomerPrediction]
    total: int
    page: int
    page_size: int


class SimulationRequest(BaseModel):
    discount_percentage: float  # 0-100
    risk_threshold: float = 0.70  # Only target customers above this probability


class SimulationResponse(BaseModel):
    customers_targeted: int
    original_revenue_at_risk: float
    discount_cost: float
    projected_retained_revenue: float
    net_savings: float
    projection_without_intervention: list[float]
    projection_with_intervention: list[float]


class RetrainResponse(BaseModel):
    status: str
    roc_auc: float | None = None
    brier_score: float | None = None
    psi_monthly_charges: float | None = None
    train_size: int | None = None
    test_size: int | None = None
    message: str



class CustomerDeepDiveResponse(BaseModel):
    customer_id: str
    monthly_charges: float
    total_charges: float
    tenure: int
    contract: str
    payment_method: str
    internet_service: str
    churn_probability: float
    shap_base_value: float
    shap_contributions: list[dict]

class SegmentationResponse(BaseModel):
    contract_risk: list[dict]
    internet_risk: list[dict]
    payment_risk: list[dict]
    value_matrix: list[dict]

class ActionResponse(BaseModel):
    status: str
    message: str

# ─── Global State for Background Training ─────────────────────────────────────
training_status = {
    "is_training": False,
    "last_result": None
}

def run_training_task():
    global training_status
    try:
        metrics = train_and_predict()
        training_status["last_result"] = {
            "status": "success",
            "roc_auc": metrics["roc_auc"],
            "brier_score": metrics["brier_score"],
            "psi_monthly_charges": metrics["psi_monthly_charges"],
            "train_size": metrics["train_size"],
            "test_size": metrics["test_size"],
            "message": "Model successfully retrained. New predictions saved to database.",
        }
    except Exception as e:
        logger.exception("Retrain failed")
        training_status["last_result"] = {
            "status": "error",
            "message": f"Retrain failed: {str(e)}",
        }
    finally:
        training_status["is_training"] = False


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Returns high-level KPIs and drift metrics for the dashboard overview."""

    # Total customers & avg churn risk
    result = await db.execute(
        select(
            func.count(Prediction.customer_id),
            func.sum(Prediction.monthly_charges),
            func.avg(Prediction.churn_probability),
        )
    )
    row = result.one()
    total_customers = row[0] or 0
    total_revenue = round(float(row[1] or 0), 2)
    avg_churn_risk = round(float(row[2] or 0), 4)

    # Revenue at risk (sum of monthly charges where probability > 0.5)
    risk_result = await db.execute(
        select(func.sum(Prediction.monthly_charges)).where(
            Prediction.churn_probability > 0.5
        )
    )
    revenue_at_risk = round(float(risk_result.scalar() or 0), 2)

    # Model metadata
    meta_result = await db.execute(
        select(ModelMetadata).where(ModelMetadata.is_active == True).order_by(
            ModelMetadata.trained_at.desc()
        ).limit(1)
    )
    meta = meta_result.scalar_one_or_none()

    psi_score = meta.psi_monthly_charges if meta else 0.0
    if psi_score < 0.1:
        drift_status = "Stable"
    elif psi_score < 0.25:
        drift_status = "Warning"
    else:
        drift_status = "Critical"

    return DashboardSummary(
        total_customers=total_customers,
        total_revenue=total_revenue,
        revenue_at_risk=revenue_at_risk,
        avg_churn_risk=avg_churn_risk,
        model_roc_auc=round(meta.roc_auc, 4) if meta else None,
        model_brier_score=round(meta.brier_score, 4) if meta else None,
        drift_metrics=DriftMetrics(
            feature="MonthlyCharges",
            psi_score=round(psi_score, 4),
            status=drift_status,
        ),
    )


@router.get("/customers", response_model=CustomerListResponse)
async def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort_by: str = Query("churn_probability", enum=["churn_probability", "monthly_charges", "customer_id"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    min_risk: float = Query(0.0, ge=0.0, le=1.0),
    search: str | None = Query(None, description="Search by customer ID"),
    db: AsyncSession = Depends(get_db),
):
    """Returns a paginated, sortable list of customer predictions."""

    # Build query
    base_query = select(Prediction).where(Prediction.churn_probability >= min_risk)
    
    # Search
    if search:
        base_query = base_query.where(Prediction.customer_id.ilike(f"%{search}%"))

    # Sorting
    sort_col = getattr(Prediction, sort_by)
    if sort_order == "desc":
        base_query = base_query.order_by(sort_col.desc())
    else:
        base_query = base_query.order_by(sort_col.asc())

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    paginated = base_query.offset(offset).limit(page_size)
    result = await db.execute(paginated)
    predictions = result.scalars().all()

    customers = [
        CustomerPrediction(
            customer_id=p.customer_id,
            monthly_charges=round(p.monthly_charges, 2),
            actual_churn=p.actual_churn,
            churn_probability=round(p.churn_probability, 4),
            lower_bound=round(p.lower_bound, 4),
            upper_bound=round(p.upper_bound, 4),
            top_drivers=[p.top_driver_1, p.top_driver_2, p.top_driver_3],
        )
        for p in predictions
    ]

    return CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/simulate-discount", response_model=SimulationResponse)
async def simulate_discount(
    req: SimulationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    What-If simulator: Given a discount % and a risk threshold,
    calculate how much revenue we could retain, and generate 6-month projections.
    """
    # Get total revenue for projections
    total_result = await db.execute(select(func.sum(Prediction.monthly_charges)))
    total_revenue = float(total_result.scalar() or 0)
    
    result = await db.execute(
        select(
            Prediction.monthly_charges,
            Prediction.churn_probability,
        ).where(Prediction.churn_probability >= req.risk_threshold)
    )
    at_risk = result.all()

    if not at_risk:
        return SimulationResponse(
            customers_targeted=0,
            original_revenue_at_risk=0,
            discount_cost=0,
            projected_retained_revenue=0,
            net_savings=0,
            projection_without_intervention=[total_revenue]*6,
            projection_with_intervention=[total_revenue]*6,
        )

    customers_targeted = len(at_risk)
    original_revenue = sum(row.monthly_charges for row in at_risk)

    # Discount cost: what we give away
    discount_cost = original_revenue * (req.discount_percentage / 100)

    # Retention model: Each 1% discount retains ~6% of at-risk revenue (capped at 90%)
    retention_rate = min(0.90, (req.discount_percentage / 100) * 6)
    projected_retained = original_revenue * retention_rate

    net_savings = projected_retained - discount_cost
    
    # 6-month projections
    proj_without = []
    proj_with = []
    for month in range(6):
        # Without intervention: we lose 15% of the original at-risk revenue each month until it's gone
        loss = original_revenue * min(1.0, 0.15 * month)
        proj_without.append(round(total_revenue - loss, 2))
        
        # With intervention: we save some of that loss, scaled over time
        saved = net_savings * (month / 5.0) 
        proj_with.append(round(total_revenue - loss + saved, 2))

    return SimulationResponse(
        customers_targeted=customers_targeted,
        original_revenue_at_risk=round(original_revenue, 2),
        discount_cost=round(discount_cost, 2),
        projected_retained_revenue=round(projected_retained, 2),
        net_savings=round(net_savings, 2),
        projection_without_intervention=proj_without,
        projection_with_intervention=proj_with,
    )


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_model(background_tasks: BackgroundTasks):
    """
    Triggers a full model retrain as a background task to prevent timeouts.
    """
    global training_status
    if training_status["is_training"]:
        return RetrainResponse(status="training", message="Training already in progress.")
    
    training_status["is_training"] = True
    background_tasks.add_task(run_training_task)
    return RetrainResponse(status="training_started", message="Model retraining started in the background.")


@router.get("/model-status", response_model=RetrainResponse)
async def get_model_status():
    """Returns the status of the background model training."""
    global training_status
    if training_status["is_training"]:
        return RetrainResponse(status="training", message="Training in progress...")
    if training_status["last_result"]:
        return RetrainResponse(**training_status["last_result"])
    return RetrainResponse(status="idle", message="No active training task.")

from app.models import Customer
from app.ml_engine import explain_customer

@router.get("/customer/{customer_id}", response_model=CustomerDeepDiveResponse)
async def get_customer_deep_dive(customer_id: str, db: AsyncSession = Depends(get_db)):
    # Get raw customer
    c_res = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    customer = c_res.scalar_one_or_none()
    if not customer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
        
    # Get prediction
    p_res = await db.execute(select(Prediction).where(Prediction.customer_id == customer_id))
    pred = p_res.scalar_one_or_none()
    
    # Get SHAP
    try:
        shap_data = explain_customer(customer_id)
    except Exception as e:
        logger.error(f"SHAP error: {e}")
        shap_data = {"base_value": 0, "contributions": []}
        
    return CustomerDeepDiveResponse(
        customer_id=customer.customer_id,
        monthly_charges=customer.monthly_charges,
        total_charges=customer.total_charges,
        tenure=customer.tenure,
        contract=customer.contract,
        payment_method=customer.payment_method,
        internet_service=customer.internet_service,
        churn_probability=pred.churn_probability if pred else 0.0,
        shap_base_value=shap_data["base_value"],
        shap_contributions=shap_data["contributions"]
    )

@router.get("/segmentation", response_model=SegmentationResponse)
async def get_segmentation(db: AsyncSession = Depends(get_db)):
    # Helper to get average risk by a column
    async def avg_risk_by(col_name):
        col = getattr(Customer, col_name)
        res = await db.execute(
            select(col, func.avg(Prediction.churn_probability))
            .join(Prediction, Customer.customer_id == Prediction.customer_id)
            .group_by(col)
        )
        return [{"segment": row[0], "avg_risk": float(row[1] or 0)} for row in res.all()]

    contract_risk = await avg_risk_by("contract")
    internet_risk = await avg_risk_by("internet_service")
    payment_risk = await avg_risk_by("payment_method")
    
    # Value matrix: take a random sample of 200 customers to plot
    # We need monthly_charges, churn_probability, and contract
    vm_res = await db.execute(
        select(Customer.customer_id, Customer.monthly_charges, Prediction.churn_probability, Customer.contract)
        .join(Prediction, Customer.customer_id == Prediction.customer_id)
        .limit(200)
    )
    value_matrix = [
        {
            "id": r[0],
            "monthly_charges": float(r[1]),
            "churn_probability": float(r[2]),
            "contract": r[3]
        }
        for r in vm_res.all()
    ]
    
    return SegmentationResponse(
        contract_risk=contract_risk,
        internet_risk=internet_risk,
        payment_risk=payment_risk,
        value_matrix=value_matrix
    )

@router.post("/trigger-campaign", response_model=ActionResponse)
async def trigger_campaign(customer_id: str):
    import asyncio
    # Simulate API call to SendGrid or Salesforce
    await asyncio.sleep(1)
    return ActionResponse(status="success", message=f"Retention campaign triggered for {customer_id}")
