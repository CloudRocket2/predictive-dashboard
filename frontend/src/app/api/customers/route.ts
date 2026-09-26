import { NextResponse, NextRequest } from 'next/server';
import pool from '@/lib/db';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get('page') || '1');
  const pageSize = parseInt(searchParams.get('page_size') || '50');
  const minRisk = parseFloat(searchParams.get('min_risk') || '0');
  const sortBy = searchParams.get('sort_by') || 'churn_probability';
  const sortOrder = searchParams.get('sort_order') || 'desc';
  const search = searchParams.get('search') || '';

  try {
    let whereClause = 'WHERE p.churn_probability >= $1';
    const values: any[] = [minRisk];

    if (search) {
      whereClause += ' AND c.customer_id ILIKE $2';
      values.push(`%${search}%`);
    }

    const orderDirection = sortOrder === 'asc' ? 'ASC' : 'DESC';
    let sortColumn = 'p.churn_probability';
    if (sortBy === 'customer_id') sortColumn = 'c.customer_id';
    else if (sortBy === 'monthly_charges') sortColumn = 'p.monthly_charges';
    
    // Count total
    const countQuery = `
      SELECT COUNT(*) 
      FROM predictions p
      JOIN customers c ON p.customer_id = c.customer_id
      ${whereClause}
    `;
    const { rows: countRows } = await pool.query(countQuery, values);
    const total = parseInt(countRows[0].count);

    // Fetch data
    const offset = (page - 1) * pageSize;
    values.push(pageSize, offset);
    
    const dataQuery = `
      SELECT 
        p.customer_id, p.monthly_charges, p.actual_churn, 
        p.churn_probability, p.lower_bound, p.upper_bound,
        p.top_driver_1, p.top_driver_2, p.top_driver_3
      FROM predictions p
      JOIN customers c ON p.customer_id = c.customer_id
      ${whereClause}
      ORDER BY ${sortColumn} ${orderDirection}
      LIMIT $${values.length - 1} OFFSET $${values.length}
    `;
    
    const { rows } = await pool.query(dataQuery, values);

    const customers = rows.map(r => ({
      customer_id: r.customer_id,
      monthly_charges: parseFloat(r.monthly_charges),
      actual_churn: r.actual_churn,
      churn_probability: parseFloat(r.churn_probability),
      lower_bound: parseFloat(r.lower_bound),
      upper_bound: parseFloat(r.upper_bound),
      top_drivers: [r.top_driver_1, r.top_driver_2, r.top_driver_3].filter(Boolean)
    }));

    return NextResponse.json({
      customers,
      total,
      page,
      page_size: pageSize
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to fetch customers' }, { status: 500 });
  }
}
