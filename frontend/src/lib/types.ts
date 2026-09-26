export interface CustomerPrediction {
  customer_id: string;
  monthly_charges: number;
  actual_churn: number;
  churn_probability: number;
  lower_bound: number;
  upper_bound: number;
  top_drivers: string[];
}

export interface CustomerListResponse {
  customers: CustomerPrediction[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardSummary {
  total_customers: number;
  total_revenue: number;
  revenue_at_risk: number;
  avg_churn_risk: number;
  model_roc_auc: number | null;
  model_brier_score: number | null;
  drift_metrics: {
    feature: string;
    psi_score: number;
    status: string;
  };
}

export interface SimulationResponse {
  customers_targeted: number;
  original_revenue_at_risk: number;
  discount_cost: number;
  projected_retained_revenue: number;
  net_savings: number;
  projection_without_intervention: number[];
  projection_with_intervention: number[];
}

export interface RetrainResponse {
  status: 'training_started' | 'training' | 'success' | 'error' | 'idle';
  roc_auc?: number;
  brier_score?: number;
  psi_monthly_charges?: number;
  train_size?: number;
  test_size?: number;
  message: string;
}

export interface CustomerDeepDiveResponse {
  customer_id: string;
  monthly_charges: number;
  total_charges: number;
  tenure: number;
  contract: string;
  payment_method: string;
  internet_service: string;
  churn_probability: number;
  shap_base_value: number;
  shap_contributions: Array<{feature: string, value: number}>;
}

export interface SegmentationResponse {
  contract_risk: Array<{segment: string, avg_risk: number}>;
  internet_risk: Array<{segment: string, avg_risk: number}>;
  payment_risk: Array<{segment: string, avg_risk: number}>;
  value_matrix: Array<{id: string, monthly_charges: number, churn_probability: number, contract: string}>;
}

export interface ActionResponse {
  status: string;
  message: string;
}
