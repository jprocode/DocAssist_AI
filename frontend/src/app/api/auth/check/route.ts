import { NextRequest, NextResponse } from 'next/server';

const PASSWORD_COOKIE = 'docassist_auth';

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIP = request.headers.get('x-real-ip');
  return forwarded?.split(',')[0] || realIP || 'unknown';
}

export async function GET(request: NextRequest) {
  const isAuthenticated = request.cookies.get(PASSWORD_COOKIE)?.value === 'authenticated';
  const ip = getClientIP(request);
  const userAgent = request.headers.get('user-agent') || 'Unknown';
  
  // Log authentication check (for security monitoring)
  if (!isAuthenticated) {
    console.info(`[SECURITY] Authentication check failed - IP: ${ip}, User-Agent: ${userAgent}`);
  }
  
  if (isAuthenticated) {
    return NextResponse.json({ authenticated: true });
  } else {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
}

