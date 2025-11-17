# Deployment Guide

## Security Features Implemented

### 1. Password Protection
- **Password**: `qwieudnvvnru2849shsshUIBDYIWNND8R93SUIe!!!!!1122123`
- All routes are protected by Next.js middleware
- Authentication cookie expires after 30 days
- Logout functionality available in sidebar

### 2. Rate Limiting
- **Upload Endpoint**: 5 uploads per hour per IP address
- **Ask Endpoint**: 20 requests per minute per IP address
- Prevents abuse and excessive API usage

### 3. File Upload Security
- Maximum file size: 50MB
- Only PDF files accepted
- File type validation on both frontend and backend

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
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app/api
   ```
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

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL=https://your-backend-url/api`

## Post-Deployment Checklist

- [ ] Test password protection works
- [ ] Test file upload functionality
- [ ] Test chat with Dr.Doc
- [ ] Verify rate limiting works
- [ ] Check CORS is properly configured
- [ ] Monitor OpenAI API usage
- [ ] Test logout functionality

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
- Verify password in `frontend/src/app/api/auth/login/route.ts` matches your desired password

