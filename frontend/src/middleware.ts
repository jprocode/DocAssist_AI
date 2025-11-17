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
    const response = NextResponse.next();
    addSecurityHeaders(response, request);
    return response;
  }

  // Protect all routes except auth
  if (!isAuthenticated) {
    // Redirect to auth page
    return NextResponse.redirect(new URL('/auth', request.url));
  }

  const response = NextResponse.next();
  addSecurityHeaders(response, request);
  return response;
}

function addSecurityHeaders(response: NextResponse, request: NextRequest) {
  const isProduction = process.env.NODE_ENV === 'production';
  
  // Security headers
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  if (isProduction) {
    // HSTS only in production
    response.headers.set(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains'
    );
  }
  
  // Content Security Policy
  const isDevelopment = process.env.NODE_ENV === 'development';
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const backendOrigin = backendUrl.replace('/api', ''); // Extract origin from API URL
  
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // Next.js requires unsafe-eval and unsafe-inline
    "style-src 'self' 'unsafe-inline'", // Tailwind requires unsafe-inline
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    isDevelopment 
      ? `connect-src 'self' ${backendOrigin} http://localhost:8000` // Allow backend in development
      : "connect-src 'self'", // Production: only same origin
    "frame-ancestors 'none'",
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', csp);
  
  return response;
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

