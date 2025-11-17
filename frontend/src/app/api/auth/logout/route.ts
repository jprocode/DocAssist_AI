import { NextRequest, NextResponse } from 'next/server';

const PASSWORD_COOKIE = 'docassist_auth';

export async function POST(request: NextRequest) {
  const response = NextResponse.redirect(new URL('/auth', request.url));
  
  // Clear authentication cookie
  response.cookies.delete(PASSWORD_COOKIE);

  return response;
}

export async function GET(request: NextRequest) {
  const response = NextResponse.redirect(new URL('/auth', request.url));
  
  // Clear authentication cookie
  response.cookies.delete(PASSWORD_COOKIE);

  return response;
}

