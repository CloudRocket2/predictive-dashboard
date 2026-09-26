import { NextResponse } from 'next/server';

export async function POST() {
  // We simulate "LLM Knowledge Base Sync" taking a few seconds
  global.isTraining = true;
  global.trainingStartedAt = Date.now();
  
  return NextResponse.json({
    status: "training_started",
    message: "LLM Knowledge Base sync started..."
  });
}
