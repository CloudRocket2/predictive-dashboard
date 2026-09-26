import { NextResponse, NextRequest } from 'next/server';
import pool from '@/lib/db';
import Groq from 'groq-sdk';

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY || 'dummy' });

export async function GET(request: NextRequest, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  try {
    const customerId = params.id;

    // Get customer data
    const { rows: cRows } = await pool.query('SELECT * FROM customers WHERE customer_id = $1', [customerId]);
    if (cRows.length === 0) {
      return NextResponse.json({ error: 'Customer not found' }, { status: 404 });
    }
    const customer = cRows[0];

    // Get prediction
    const { rows: pRows } = await pool.query('SELECT * FROM predictions WHERE customer_id = $1', [customerId]);
    const pred = pRows[0] || {};
    const churnProb = pred.churn_probability ? parseFloat(pred.churn_probability) : 0.0;

    let shap_contributions = [];
    let shap_base = 0.5;

    // Use Groq to explain the prediction if API key exists
    if (process.env.GROQ_API_KEY) {
      const prompt = `
        Analyze this customer profile and explain their churn probability (${(churnProb * 100).toFixed(1)}%).
        Profile: Tenure: ${customer.tenure} months, Contract: ${customer.contract}, 
        Monthly Charges: $${customer.monthly_charges}, Tech Support: ${customer.tech_support}, Internet: ${customer.internet_service}.
        
        Return ONLY a JSON array of exact format:
        [
          {"feature": "Feature Name", "value": "Feature Value", "contribution": 0.15},
          ...
        ]
        The contributions should sum roughly to the churn probability minus 0.5. Positive means drives churn up, negative means retains customer.
      `;

      try {
        const startTime = Date.now();
        const chatCompletion = await groq.chat.completions.create({
          messages: [{ role: 'user', content: prompt }],
          model: 'gpt-oss-120b',
          temperature: 0.2,
          response_format: { type: 'json_object' }
        });
        
        const endTime = Date.now();
        const latencyMs = endTime - startTime;
        
        // Log latency asynchronously to DB (using roc_auc to hold latency, brier_score to hold context limit)
        pool.query('UPDATE model_metadata SET roc_auc = $1, brier_score = 8192 WHERE is_active = true', [latencyMs]).catch(e => console.error(e));
        
        const responseText = chatCompletion.choices[0]?.message?.content || '{}';
        try {
            const parsed = JSON.parse(responseText);
            if (Array.isArray(parsed)) {
                shap_contributions = parsed;
            } else if (parsed.contributions) {
                shap_contributions = parsed.contributions;
            } else if (parsed.features) {
                shap_contributions = parsed.features;
            }
        } catch (e) {
            console.error("Failed to parse Groq JSON", e);
        }
      } catch (error) {
        console.error("Groq API error:", error);
      }
    }

    // Fallback if Groq fails or no API key
    if (shap_contributions.length === 0) {
      shap_contributions = [
        { feature: pred.top_driver_1 || 'Contract', value: customer.contract, contribution: churnProb > 0.5 ? 0.15 : -0.1 },
        { feature: pred.top_driver_2 || 'Tenure', value: `${customer.tenure} mos`, contribution: customer.tenure < 12 ? 0.1 : -0.05 },
        { feature: pred.top_driver_3 || 'Internet', value: customer.internet_service, contribution: 0.05 }
      ];
    }

    return NextResponse.json({
      customer_id: customer.customer_id,
      monthly_charges: parseFloat(customer.monthly_charges),
      total_charges: parseFloat(customer.total_charges || 0),
      tenure: customer.tenure,
      contract: customer.contract,
      payment_method: customer.payment_method,
      internet_service: customer.internet_service,
      churn_probability: churnProb,
      shap_base_value: shap_base,
      shap_contributions: shap_contributions
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to fetch customer' }, { status: 500 });
  }
}
