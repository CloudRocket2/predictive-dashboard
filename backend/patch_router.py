import re

with open('app/routers/dashboard.py', 'r') as f:
    content = f.read()

# Add schemas
schemas = """
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
"""

if "CustomerDeepDiveResponse" not in content:
    content = content.replace("# ─── Global State", schemas + "\n# ─── Global State")

# Add endpoints
endpoints = """
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
"""

if "@router.get(\"/customer/{customer_id}\"" not in content:
    content += endpoints
    with open('app/routers/dashboard.py', 'w') as f:
        f.write(content)
        print("Patched router")
else:
    print("Already patched")
