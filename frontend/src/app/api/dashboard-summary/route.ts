import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const { rows: totalRows } = await pool.query('SELECT COUNT(*) FROM customers');
    const totalCustomers = parseInt(totalRows[0].count);

    const { rows: revRows } = await pool.query('SELECT SUM(monthly_charges) as total FROM customers');
    const totalRevenue = parseFloat(revRows[0].total || 0);

    const { rows: riskRevRows } = await pool.query('SELECT SUM(p.monthly_charges) as risk_total FROM predictions p WHERE p.churn_probability > 0.5');
    const revenueAtRisk = parseFloat(riskRevRows[0].risk_total || 0);

    const { rows: riskRows } = await pool.query('SELECT AVG(churn_probability) as avg_risk FROM predictions');
    const avgRisk = parseFloat(riskRows[0].avg_risk || 0);

    const { rows: modelRows } = await pool.query('SELECT * FROM model_metadata WHERE is_active = true LIMIT 1');
    const model = modelRows[0] || {};
    
    let status = 'Stable';
    if (model.psi_monthly_charges > 0.1 && model.psi_monthly_charges <= 0.2) status = 'Warning';
    else if (model.psi_monthly_charges > 0.2) status = 'Critical';

    return NextResponse.json({
      total_customers: totalCustomers,
      total_revenue: totalRevenue,
      revenue_at_risk: revenueAtRisk,
      avg_churn_risk: avgRisk,
      model_roc_auc: model.roc_auc || null,
      model_brier_score: model.brier_score || null,
      drift_metrics: {
        feature: 'MonthlyCharges',
        psi_score: model.psi_monthly_charges || 0,
        status: status
      }
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to fetch summary' }, { status: 500 });
  }
}
