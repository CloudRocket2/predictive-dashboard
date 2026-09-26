import { NextResponse } from 'next/server';

export async function GET() {
  if (global.isTraining) {
    const elapsed = Date.now() - (global.trainingStartedAt || 0);
    if (elapsed > 5000) { // 5 seconds to mock completion
      global.isTraining = false;
      return NextResponse.json({
        status: "completed",
        message: "LLM Sync completed. Groq accuracy optimized.",
        metrics: {
          roc_auc: 0.96,
          brier_score: 0.08,
          psi: 0.01
        }
      });
    }
    return NextResponse.json({
      status: "training",
      message: "Syncing Knowledge Base..."
    });
  }
  return NextResponse.json({
    status: "idle",
    message: "System ready."
  });
}
