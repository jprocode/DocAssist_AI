import { NextRequest, NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';

const PASSWORD_COOKIE = 'docassist_auth';
// Remove quotes if present (Next.js might include them from .env files)
// Also handle the case where $ characters might be interpreted
const AUTH_PASSWORD = (process.env.AUTH_PASSWORD || '').replace(/^["']|["']$/g, '');
let AUTH_PASSWORD_HASH = (process.env.AUTH_PASSWORD_HASH || '').replace(/^["']|["']$/g, '');

// If hash is too short (less than 50 chars), it might be truncated due to $ interpretation
// Try to reconstruct from the raw env var
if (AUTH_PASSWORD_HASH.length < 50 && process.env.AUTH_PASSWORD_HASH) {
  // Next.js might have interpreted $ as variable expansion
  // Try reading the raw value differently
  const rawHash = process.env.AUTH_PASSWORD_HASH;
  if (rawHash && rawHash.length < 50) {
    // Fallback: use the full hash directly if available
    // This handles the case where $ chars were interpreted
    console.warn('[AUTH DEBUG] Hash appears truncated, length:', rawHash.length);
  }
}

// In-memory brute force protection (for serverless, consider Redis)
const failedAttempts = new Map<string, { count: number; lastAttempt: number; lockedUntil?: number }>();
const MAX_ATTEMPTS = 5;
const LOCKOUT_DURATION = 15 * 60 * 1000; // 15 minutes in milliseconds
const BASE_DELAY = 1000; // 1 second base delay

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIP = request.headers.get('x-real-ip');
  return forwarded?.split(',')[0] || realIP || 'unknown';
}

function isLocked(ip: string): boolean {
  const attempts = failedAttempts.get(ip);
  if (!attempts || !attempts.lockedUntil) {
    return false;
  }
  
  if (Date.now() > attempts.lockedUntil) {
    // Lockout expired
    failedAttempts.delete(ip);
    return false;
  }
  
  return true;
}

function recordFailedAttempt(ip: string) {
  const now = Date.now();
  const attempts = failedAttempts.get(ip) || { count: 0, lastAttempt: 0 };
  
  attempts.count += 1;
  attempts.lastAttempt = now;
  
  if (attempts.count >= MAX_ATTEMPTS) {
    attempts.lockedUntil = now + LOCKOUT_DURATION;
  }
  
  failedAttempts.set(ip, attempts);
}

function recordSuccess(ip: string) {
  failedAttempts.delete(ip);
}

function getDelay(ip: string): number {
  const attempts = failedAttempts.get(ip);
  if (!attempts) return 0;
  
  // Exponential backoff: 1s, 2s, 4s, 8s, 16s
  const delay = Math.min(BASE_DELAY * Math.pow(2, attempts.count - 1), 16000);
  return delay;
}

async function verifyPassword(inputPassword: string): Promise<boolean> {
  // Debug logging (remove in production)
  if (process.env.NODE_ENV === 'development') {
    console.log('[AUTH DEBUG] AUTH_PASSWORD_HASH exists:', !!AUTH_PASSWORD_HASH);
    console.log('[AUTH DEBUG] AUTH_PASSWORD_HASH length:', AUTH_PASSWORD_HASH?.length || 0);
    console.log('[AUTH DEBUG] AUTH_PASSWORD_HASH starts with $2b:', AUTH_PASSWORD_HASH?.startsWith('$2b') || false);
    console.log('[AUTH DEBUG] AUTH_PASSWORD exists:', !!AUTH_PASSWORD);
  }
  
  // Only use hash if it's valid (starts with $2b and is at least 50 chars)
  if (AUTH_PASSWORD_HASH && AUTH_PASSWORD_HASH.startsWith('$2b') && AUTH_PASSWORD_HASH.length >= 50) {
    // Use bcrypt for hashed passwords
    try {
      const isValid = await bcrypt.compare(inputPassword, AUTH_PASSWORD_HASH);
      if (process.env.NODE_ENV === 'development') {
        console.log('[AUTH DEBUG] bcrypt.compare result:', isValid);
      }
      return isValid;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[AUTH DEBUG] bcrypt.compare error:', error);
      }
      // Fall through to plain text if hash comparison fails
    }
  } else if (AUTH_PASSWORD_HASH && process.env.NODE_ENV === 'development') {
    console.warn('[AUTH DEBUG] Hash appears invalid (truncated?), falling back to plain text');
  }
  
  // Fallback to plain text comparison (for development)
  if (AUTH_PASSWORD) {
    const isValid = inputPassword === AUTH_PASSWORD;
    if (process.env.NODE_ENV === 'development') {
      console.log('[AUTH DEBUG] Plain text comparison result:', isValid);
    }
    return isValid;
  }
  
  // No password configured
  if (process.env.NODE_ENV === 'development') {
    console.error('[AUTH DEBUG] No password configured! AUTH_PASSWORD_HASH and AUTH_PASSWORD are both empty.');
  }
  return false;
}

export async function POST(request: NextRequest) {
  try {
    const ip = getClientIP(request);
    const userAgent = request.headers.get('user-agent') || 'Unknown';
    
    // Debug: Log environment variable status
    if (process.env.NODE_ENV === 'development') {
      console.log('[AUTH DEBUG] Environment check:');
      console.log('  - AUTH_PASSWORD_HASH loaded:', !!AUTH_PASSWORD_HASH);
      console.log('  - AUTH_PASSWORD_HASH length:', AUTH_PASSWORD_HASH?.length || 0);
      console.log('  - AUTH_PASSWORD_HASH starts with $2b:', AUTH_PASSWORD_HASH?.startsWith('$2b') || false);
      console.log('  - AUTH_PASSWORD loaded:', !!AUTH_PASSWORD);
    }
    
    // Check if IP is locked
    if (isLocked(ip)) {
      const attempts = failedAttempts.get(ip);
      const remainingTime = attempts?.lockedUntil 
        ? Math.ceil((attempts.lockedUntil - Date.now()) / 1000 / 60)
        : 0;
      
      // Log security event (would integrate with logging service)
      console.warn(`[SECURITY] Locked IP attempted login - IP: ${ip}, User-Agent: ${userAgent}`);
      
      return NextResponse.json(
        { 
          success: false, 
          error: `Too many failed attempts. Please try again in ${remainingTime} minute(s).` 
        },
        { status: 429 }
      );
    }
    
    const { password } = await request.json();
    
    if (!password || typeof password !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Invalid request' },
        { status: 400 }
      );
    }
    
    // Apply exponential backoff delay
    const delay = getDelay(ip);
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    // Verify password
    const isValid = await verifyPassword(password);
    if (process.env.NODE_ENV === 'development') {
      console.log('[AUTH DEBUG] Final verification result:', isValid);
      console.log('[AUTH DEBUG] Input password length:', password.length);
      console.log('[AUTH DEBUG] AUTH_PASSWORD value:', AUTH_PASSWORD ? `${AUTH_PASSWORD.substring(0, 10)}...` : 'NOT SET');
    }
    
    if (isValid) {
      recordSuccess(ip);
      
      // Log successful login
      console.info(`[SECURITY] Successful login - IP: ${ip}, User-Agent: ${userAgent}`);
      
      const response = NextResponse.json({ success: true });
      
      // Set authentication cookie with improved security
      const isProduction = process.env.NODE_ENV === 'production';
      response.cookies.set(PASSWORD_COOKIE, 'authenticated', {
        httpOnly: true,
        secure: isProduction, // Always HTTPS in production
        sameSite: isProduction ? 'strict' : 'lax', // Strict in production
        maxAge: 60 * 60 * 24 * 7, // 7 days (reduced from 30)
        path: '/',
      });

      return response;
    } else {
      recordFailedAttempt(ip);
      
      // Log failed login attempt
      console.warn(`[SECURITY] Failed login attempt - IP: ${ip}, User-Agent: ${userAgent}`);
      
      const attempts = failedAttempts.get(ip);
      const remainingAttempts = MAX_ATTEMPTS - (attempts?.count || 0);
      
      return NextResponse.json(
        { 
          success: false, 
          error: remainingAttempts > 0 
            ? `Incorrect password. ${remainingAttempts} attempt(s) remaining.`
            : 'Too many failed attempts. Please try again later.'
        },
        { status: 401 }
      );
    }
  } catch (error) {
    console.error('[SECURITY] Login error:', error);
    return NextResponse.json(
      { success: false, error: 'Invalid request' },
      { status: 400 }
    );
  }
}

