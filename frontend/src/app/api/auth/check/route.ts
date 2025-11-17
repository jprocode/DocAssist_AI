import { NextRequest, NextResponse } from 'next/server';

const PASSWORD_COOKIE = 'docassist_auth';

export async function GET(request: NextRequest) {
  const isAuthenticated = request.cookies.get(PASSWORD_COOKIE)?.value === 'authenticated';
  
  if (isAuthenticated) {
    return NextResponse.json({ authenticated: true });
  } else {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
}

