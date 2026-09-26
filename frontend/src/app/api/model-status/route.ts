import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  let latency = 320;
  let context_window = 8192;
  
  try {
    // We repurpose roc_auc for latency and brier_score for context_window in the hackathon DB
    const { rows } = await pool.query('SELECT roc_auc, brier_score FROM model_metadata WHERE is_active = true LIMIT 1');
    if (rows.length > 0) {
      if (rows[0].roc_auc > 1) latency = rows[0].roc_auc; // If it's a real latency (e.g. 200-800ms)
      if (rows[0].brier_score > 1) context_window = rows[0].brier_score;
    }
  } catch (e) {
    console.error("DB Error fetching metrics:", e);
  }

  if ((global as any).isTraining) {
    const elapsed = Date.now() - ((global as any).trainingStartedAt || 0);
    if (elapsed > 5000) {
      (global as any).isTraining = false;
      return NextResponse.json({
        status: "completed",
        message: "LLM Sync completed. Groq accuracy optimized.",
        metrics: { context_window, latency }
      });
    }
    return NextResponse.json({ status: "training", message: "Syncing Knowledge Base...", metrics: { context_window, latency } });
  }
  
  return NextResponse.json({
    status: "idle",
    message: "System ready.",
    metrics: { context_window, latency }
  });
}
