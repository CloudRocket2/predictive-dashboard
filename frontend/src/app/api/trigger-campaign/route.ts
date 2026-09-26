import { NextResponse, NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const customerId = searchParams.get('customer_id');
  return NextResponse.json({
    status: "success",
    message: `Retention campaign triggered for ${customerId} via LLM agent.`
  });
}
