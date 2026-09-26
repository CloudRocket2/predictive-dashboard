import { NextResponse } from 'next/server';

export async function POST() {
  // We simulate "LLM Knowledge Base Sync" taking a few seconds
  (global as any).isTraining = true;
  (global as any).trainingStartedAt = Date.now();
  
  return NextResponse.json({
    status: "training_started",
    message: "LLM Knowledge Base sync started..."
  });
}
