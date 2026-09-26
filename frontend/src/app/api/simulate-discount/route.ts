import { NextResponse, NextRequest } from 'next/server';
import pool from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const { discount_percentage, risk_threshold } = await request.json();

    const { rows: totalRows } = await pool.query('SELECT SUM(monthly_charges) as total FROM predictions');
    const totalRevenue = parseFloat(totalRows[0].total || 0);

    const { rows: atRiskRows } = await pool.query(
      'SELECT monthly_charges FROM predictions WHERE churn_probability >= $1',
      [risk_threshold]
    );

    if (atRiskRows.length === 0) {
      return NextResponse.json({
        customers_targeted: 0,
        original_revenue_at_risk: 0,
        discount_cost: 0,
        projected_retained_revenue: 0,
        net_savings: 0,
        projection_without_intervention: Array(6).fill(totalRevenue),
        projection_with_intervention: Array(6).fill(totalRevenue),
      });
    }

    const customers_targeted = atRiskRows.length;
    const original_revenue = atRiskRows.reduce((sum, r) => sum + parseFloat(r.monthly_charges), 0);

    const discount_cost = original_revenue * (discount_percentage / 100);
    const retention_rate = Math.min(0.90, (discount_percentage / 100) * 6);
    const projected_retained = original_revenue * retention_rate;
    const net_savings = projected_retained - discount_cost;

    const proj_without = [];
    const proj_with = [];
    for (let month = 0; month < 6; month++) {
      const loss = original_revenue * Math.min(1.0, 0.15 * month);
      proj_without.push(parseFloat((totalRevenue - loss).toFixed(2)));
      
      const saved = net_savings * (month / 5.0);
      proj_with.push(parseFloat((totalRevenue - loss + saved).toFixed(2)));
    }

    return NextResponse.json({
      customers_targeted,
      original_revenue_at_risk: parseFloat(original_revenue.toFixed(2)),
      discount_cost: parseFloat(discount_cost.toFixed(2)),
      projected_retained_revenue: parseFloat(projected_retained.toFixed(2)),
      net_savings: parseFloat(net_savings.toFixed(2)),
      projection_without_intervention: proj_without,
      projection_with_intervention: proj_with,
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to simulate discount' }, { status: 500 });
  }
}
