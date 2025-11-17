import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PASSWORD_COOKIE = 'docassist_auth';

export function middleware(request: NextRequest) {
  // Check if user is already authenticated
  const isAuthenticated = request.cookies.get(PASSWORD_COOKIE)?.value === 'authenticated';
  
  // Allow access to auth page
  if (request.nextUrl.pathname === '/auth') {
    if (isAuthenticated) {
      // Redirect to home if already authenticated
      return NextResponse.redirect(new URL('/', request.url));
    }
    return NextResponse.next();
  }

  // Protect all routes except auth
  if (!isAuthenticated) {
    // Redirect to auth page
    return NextResponse.redirect(new URL('/auth', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

