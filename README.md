# Score Checker Web App

Production-ready web application for validating and scoring robot satisfaction output files.

## 🚀 Deployment Options

### Option 1: Railway (Recommended for Large Files)

Railway supports files up to 50MB+ and is perfect for this use case.

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Or use Railway Dashboard:**
   - Go to [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Select this repository
   - Railway will auto-detect Python and deploy

### Option 2: Render

Render also supports larger files and is free tier friendly.

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your GitHub repository
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api.index:app --bind 0.0.0.0:$PORT`
   - **Environment:** Python 3

### Option 3: Fly.io

Fly.io supports large files and has good performance.

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch`
3. Deploy: `fly deploy`

### Option 4: Keep Vercel (with limitations)

If you want to stay on Vercel, you'll need to:
- Split large files into smaller chunks
- Process files in batches
- Use a different approach for file handling

## 📦 Requirements

- Python 3.9+
- Flask 3.0.0
- Gunicorn (for production)

## 🔧 Configuration

The app is configured to handle files up to **50MB** (configurable in `api/index.py`).

## 🌐 Features

- ✅ Handles files up to 50MB
- ✅ Real-time validation and scoring
- ✅ Beautiful, modern interface
- ✅ Cross-platform (works in any browser)
- ✅ CORS enabled

## 📝 File Size Limits

- **Railway/Render/Fly.io:** 50MB+ (configurable)
- **Vercel:** 4.5MB (hard limit)

For files larger than 50MB, consider:
- Processing in chunks
- Using a dedicated file processing service
- Implementing streaming processing
