import {
  DashboardSummary,
  CustomerListResponse,
  SimulationResponse,
  RetrainResponse,
  CustomerDeepDiveResponse,
  SegmentationResponse,
  ActionResponse
} from './types';

// We now call Next.js API routes natively!
export const BASE_URL = '';

async function handleResponse<T>(response: Response, errorMessage: string): Promise<T> {
  if (!response.ok) {
    const errorBody = await response.text();
    console.error(`${errorMessage}: ${response.status} ${response.statusText}`, errorBody);
    throw new Error(`${errorMessage} (${response.status})`);
  }
  return response.json();
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const response = await fetch(`${BASE_URL}/api/dashboard-summary`);
  return handleResponse<DashboardSummary>(response, 'Failed to fetch dashboard summary');
}

export async function fetchCustomers(
  page: number = 1,
  pageSize: number = 50,
  minRisk: number = 0.0,
  sortBy: string = 'churn_probability',
  sortOrder: 'asc' | 'desc' = 'desc',
  search: string = ''
): Promise<CustomerListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    min_risk: minRisk.toString(),
    sort_by: sortBy,
    sort_order: sortOrder,
  });
  
  if (search) {
    params.append('search', search);
  }

  const response = await fetch(`${BASE_URL}/api/customers?${params.toString()}`);
  return handleResponse<CustomerListResponse>(response, 'Failed to fetch customers');
}

export async function simulateDiscount(discountPercentage: number, riskThreshold: number): Promise<SimulationResponse> {
  const response = await fetch(`${BASE_URL}/api/simulate-discount`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ discount_percentage: discountPercentage, risk_threshold: riskThreshold }),
  });
  return handleResponse<SimulationResponse>(response, 'Failed to simulate discount');
}

export async function retrainModel(): Promise<RetrainResponse> {
  const response = await fetch(`${BASE_URL}/api/retrain`, { method: 'POST' });
  return handleResponse<RetrainResponse>(response, 'Failed to retrain model');
}

export async function getModelStatus(): Promise<RetrainResponse> {
  const response = await fetch(`${BASE_URL}/api/model-status`, { cache: 'no-store' });
  return handleResponse<RetrainResponse>(response, 'Failed to get model status');
}

export async function fetchCustomerDeepDive(customerId: string): Promise<CustomerDeepDiveResponse> {
  const response = await fetch(`${BASE_URL}/api/customer/${customerId}`);
  return handleResponse<CustomerDeepDiveResponse>(response, 'Failed to fetch customer details');
}

export async function fetchSegmentation(): Promise<SegmentationResponse> {
  const response = await fetch(`${BASE_URL}/api/segmentation`);
  return handleResponse<SegmentationResponse>(response, 'Failed to fetch segmentation data');
}

export async function triggerCampaign(customerId: string): Promise<ActionResponse> {
  const response = await fetch(`${BASE_URL}/api/trigger-campaign?customer_id=${customerId}`, { method: 'POST' });
  return handleResponse<ActionResponse>(response, 'Failed to trigger campaign');
}
