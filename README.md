# Score Checker Web App - Vercel Deployment

Production-ready web application for validating and scoring robot satisfaction output files.

## 🚀 Deploy to Vercel

### Quick Deploy

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Navigate to the project folder**:
   ```bash
   cd score-checker-web
   ```

3. **Deploy**:
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Link to existing project or create new
   - Confirm settings
   - Deploy!

### Alternative: Deploy via GitHub

1. Push `score-checker-web` folder to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Set **Root Directory** to `score-checker-web`
5. Vercel will automatically detect Python
6. Click **Deploy**

## 📁 Project Structure

```
score-checker-web/
├── api/
│   └── index.py          # Serverless function (Flask app)
├── index.html            # Frontend interface
├── vercel.json           # Vercel configuration
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

The `vercel.json` file configures:
- Python serverless function at `/api/check`
- Static file serving for `index.html`
- Automatic routing

## ✨ Features

- ✅ Serverless architecture (scales automatically)
- ✅ CORS enabled for cross-origin requests
- ✅ File upload support (up to 16MB)
- ✅ Real-time validation and scoring
- ✅ Production-ready error handling

## 🌐 After Deployment

Once deployed, your app will be available at:
- `https://your-project.vercel.app`

## 📝 Environment Variables

No environment variables needed for basic functionality.

## 🧪 Testing Locally

To test locally before deploying:

```bash
pip install Flask
python api/index.py
```

Then visit `http://localhost:5000`

## 📦 Dependencies

- Flask 3.0.0 (handled automatically by Vercel)

## 🔒 Security

- File size limit: 16MB
- CORS enabled for all origins (adjust in production if needed)
- Input validation on all file contents

