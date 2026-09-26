import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const { rows: contractRows } = await pool.query(`
      SELECT c.contract as segment, AVG(p.churn_probability) as avg_risk
      FROM customers c
      JOIN predictions p ON c.customer_id = p.customer_id
      GROUP BY c.contract
    `);
    
    const { rows: internetRows } = await pool.query(`
      SELECT c.internet_service as segment, AVG(p.churn_probability) as avg_risk
      FROM customers c
      JOIN predictions p ON c.customer_id = p.customer_id
      GROUP BY c.internet_service
    `);

    const { rows: paymentRows } = await pool.query(`
      SELECT c.payment_method as segment, AVG(p.churn_probability) as avg_risk
      FROM customers c
      JOIN predictions p ON c.customer_id = p.customer_id
      GROUP BY c.payment_method
    `);

    const { rows: vmRows } = await pool.query(`
      SELECT c.customer_id, c.monthly_charges, p.churn_probability, c.contract
      FROM customers c
      JOIN predictions p ON c.customer_id = p.customer_id
      LIMIT 200
    `);

    return NextResponse.json({
      contract_risk: contractRows.map(r => ({ segment: r.segment, avg_risk: parseFloat(r.avg_risk) })),
      internet_risk: internetRows.map(r => ({ segment: r.segment, avg_risk: parseFloat(r.avg_risk) })),
      payment_risk: paymentRows.map(r => ({ segment: r.segment, avg_risk: parseFloat(r.avg_risk) })),
      value_matrix: vmRows.map(r => ({
        id: r.customer_id,
        monthly_charges: parseFloat(r.monthly_charges),
        churn_probability: parseFloat(r.churn_probability),
        contract: r.contract
      }))
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to fetch segmentation' }, { status: 500 });
  }
}
