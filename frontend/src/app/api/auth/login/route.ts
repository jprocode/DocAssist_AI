import { NextRequest, NextResponse } from 'next/server';

const PASSWORD = 'qwieudnvvnru2849shsshUIBDYIWNND8R93SUIe!!!!!1122123';
const PASSWORD_COOKIE = 'docassist_auth';

export async function POST(request: NextRequest) {
  try {
    const { password } = await request.json();

    if (password === PASSWORD) {
      const response = NextResponse.json({ success: true });
      
      // Set authentication cookie (expires in 30 days)
      response.cookies.set(PASSWORD_COOKIE, 'authenticated', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 30, // 30 days
        path: '/',
      });

      return response;
    } else {
      return NextResponse.json(
        { success: false, error: 'Invalid password' },
        { status: 401 }
      );
    }
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Invalid request' },
      { status: 400 }
    );
  }
}

