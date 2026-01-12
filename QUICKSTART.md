# Quick Start - Deploy FREE in 5 Minutes

## 🚀 Deploy to Render.com (Free - No Credit Card)

### Step 1: Fork/Push to Your GitHub
Make sure this code is in your GitHub repository.

### Step 2: Deploy to Render

1. Go to **https://dashboard.render.com**
2. Sign up/login (use GitHub login)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name**: `wheel-analyzer-api`
   - **Environment**: `Docker`
   - **Branch**: `claude/stock-options-wheel-app-JThGN` (or `main`)
   - **Plan**: `Free`
6. Click **"Create Web Service"**
7. Wait 3-5 minutes...

### Step 3: Your API is Live! 🎉

Your API URL: `https://wheel-analyzer-api.onrender.com`

Visit these URLs:
- **API Docs**: https://wheel-analyzer-api.onrender.com/docs
- **Health Check**: https://wheel-analyzer-api.onrender.com/health

## Test Your API

```bash
# Health check
curl https://wheel-analyzer-api.onrender.com/health

# Get popular tickers
curl https://wheel-analyzer-api.onrender.com/api/v1/popular-tickers

# Analyze a stock
curl "https://wheel-analyzer-api.onrender.com/api/v1/analyze/AAPL?target_dte=30"

# Find best wheel strategy candidates
curl "https://wheel-analyzer-api.onrender.com/api/v1/candidates?min_annual_return=20&max_results=5"
```

## Important Files

- **render.yaml** - One-click deployment configuration
- **Dockerfile** - Container setup
- **src/api.py** - REST API code
- **DEPLOY_FREE.md** - Full deployment guide

## Need Help?

Check the full guide: [DEPLOY_FREE.md](DEPLOY_FREE.md)

---

That's it! Your wheel strategy analyzer is now running on the cloud for FREE! 🎉
