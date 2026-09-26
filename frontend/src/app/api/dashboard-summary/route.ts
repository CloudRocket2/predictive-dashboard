import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const { rows: totalRows } = await pool.query('SELECT COUNT(*) FROM customers');
    const totalCustomers = parseInt(totalRows[0].count);

    const { rows: churnRows } = await pool.query("SELECT COUNT(*) FROM customers WHERE churn = 'Yes'");
    const totalChurned = parseInt(churnRows[0].count);

    const { rows: revRows } = await pool.query('SELECT SUM(monthly_charges) as total FROM customers');
    const totalRevenue = parseFloat(revRows[0].total || 0);

    const { rows: riskRows } = await pool.query('SELECT AVG(churn_probability) as avg_risk FROM predictions');
    const avgRisk = parseFloat(riskRows[0].avg_risk || 0) * 100; // stored as 0-1

    const { rows: recentChurnRows } = await pool.query("SELECT COUNT(*) FROM customers WHERE churn = 'Yes' AND tenure <= 1");
    const recentChurned = parseInt(recentChurnRows[0].count);

    return NextResponse.json({
      total_customers: totalCustomers,
      active_subscriptions: totalCustomers - totalChurned,
      total_mrr: totalRevenue,
      average_risk_score: avgRisk,
      recent_churns: recentChurned,
      last_updated: new Date().toISOString()
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to fetch summary' }, { status: 500 });
  }
}
