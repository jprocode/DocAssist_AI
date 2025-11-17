# Deployment Guide

## Security Features Implemented

### 1. Password Protection
- **Password Authentication**: Required to access the application
- **Password Storage**: Supports plain text (development) or bcrypt hash (production)
- **Brute Force Protection**: 5 failed attempts lock IP for 15 minutes with exponential backoff
- All routes are protected by Next.js middleware
- Authentication cookie expires after 7 days (reduced from 30)
- Cookies are httpOnly, secure in production, and SameSite=strict in production
- Logout functionality available in sidebar

### 2. Rate Limiting
- **Upload Endpoint**: 5 uploads per hour per IP address
- **Ask Endpoint**: 20 requests per minute per IP address
- **Summarize Endpoint**: 10 requests per minute per IP address
- **Documents Endpoint**: 30 requests per minute per IP address
- Rate limit headers (X-RateLimit-*) included in responses
- Prevents abuse and excessive API usage

### 3. File Upload Security
- Maximum file size: 50MB
- Only PDF files accepted
- File signature validation (magic bytes) - not just MIME type
- Filename sanitization to prevent path traversal attacks
- File type validation on both frontend and backend

### 4. Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Strict-Transport-Security (HSTS) in production
- Content-Security-Policy configured

### 5. Input Validation
- Question length limited to 2000 characters
- All inputs validated using Pydantic models
- Request body size limited to 50MB

### 6. Security Logging
- Failed login attempts logged
- Rate limit violations logged
- File upload attempts logged
- Security events logged to stdout

### 7. Operation Timeouts
- AI operations timeout after 30 seconds
- Web search timeout after 10 seconds
- Prevents hanging requests

## Deployment Steps

### Step 1: Push to GitHub

```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/docassist-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend (Railway - Recommended)

1. Go to https://railway.app and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python
5. Set environment variables:
   ```
   OPENAI_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here (optional)
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   VECTOR_DIR=/tmp/vector_store
   AUTH_PASSWORD_HASH=$2b$12$... (generate using: python backend/generate_password_hash.py your_password)
   ```
6. Note the Railway URL (e.g., `https://your-app.up.railway.app`)

### Step 3: Deploy Frontend (Vercel)

1. Go to https://vercel.com and sign up
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/.next`
5. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app/api
   AUTH_PASSWORD_HASH=$2b$12$... (same hash as backend)
   ```
   **Note**: For production, use `AUTH_PASSWORD_HASH` instead of `AUTH_PASSWORD` for better security.
6. Deploy

### Step 4: Update Backend CORS

After Vercel deployment, update Railway environment variable:
```
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

## Alternative: Render (Backend)

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add same environment variables as Railway

## Environment Variables Summary

### Backend (Railway/Render)
- `OPENAI_API_KEY` (required)
- `TAVILY_API_KEY` (optional)
- `ENVIRONMENT=production`
- `ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app`
- `VECTOR_DIR=/tmp/vector_store`
- `AUTH_PASSWORD_HASH` (recommended) or `AUTH_PASSWORD` (development only)
  - Generate hash: `python backend/generate_password_hash.py your_password`

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL=https://your-backend-url/api`
- `AUTH_PASSWORD_HASH` (recommended) or `AUTH_PASSWORD` (development only)
  - Must match backend value

## Post-Deployment Checklist

### Functionality
- [ ] Test password protection works
- [ ] Test file upload functionality
- [ ] Test chat with Dr.Doc
- [ ] Test logout functionality
- [ ] Verify rate limiting works
- [ ] Check CORS is properly configured
- [ ] Monitor OpenAI API usage

### Security Checklist
- [ ] Password is set and working (use hashed password in production)
- [ ] HTTPS is enabled (Vercel and Railway provide this automatically)
- [ ] Environment variables are set correctly (no plain text passwords in production)
- [ ] CORS is restricted to your frontend domain only
- [ ] Security headers are present (check with browser dev tools)
- [ ] Rate limiting is working (test by making rapid requests)
- [ ] File upload validation works (try uploading non-PDF file)
- [ ] Brute force protection works (try 5+ failed login attempts)
- [ ] Security logs are being generated (check Railway/Render logs)
- [ ] Error messages don't leak sensitive information
- [ ] Session cookies are secure (httpOnly, secure, SameSite=strict)

## Cost Estimates

- **Vercel**: Free tier (generous)
- **Railway**: $5/month free credit, then pay-as-you-go
- **Render**: Free tier (spins down after inactivity)
- **OpenAI API**: Pay per use (monitor in OpenAI dashboard)

## Troubleshooting

### CORS Errors
- Ensure `ALLOWED_ORIGINS` includes your exact Vercel domain
- Check that `ENVIRONMENT=production` is set

### Rate Limiting Too Strict
- Adjust limits in `backend/routers/rate_limit.py` and `backend/routers/ask.py`

### Password Not Working
- Verify `AUTH_PASSWORD` or `AUTH_PASSWORD_HASH` is set in both backend and frontend environment variables
- If using hash, ensure it matches exactly (no extra spaces)
- Check that environment variables are loaded correctly (restart services after changes)
- Generate new hash: `python backend/generate_password_hash.py your_password`

### Security Issues
- **Password exposed**: Ensure password is only in environment variables, not in code
- **CORS errors**: Check `ALLOWED_ORIGINS` includes exact frontend URL (no trailing slash)
- **Rate limiting too strict**: Adjust limits in `backend/routers/rate_limit.py` and individual router files
- **Security headers missing**: Verify middleware is running in `backend/main.py` and `frontend/src/middleware.ts`

