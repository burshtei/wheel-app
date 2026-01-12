# 🚀 Deploy to Render.com FREE in 5 Minutes

Deploy the Wheel Strategy Stock Analyzer API to Render.com's free tier - **no credit card required**!

## ✨ What You Get (FREE)

- 🌐 Live API with public URL
- 📚 Interactive API documentation
- 🔒 Free SSL certificate
- 🔄 Auto-deploy from GitHub
- 750 hours/month free (enough for 24/7 if you have other free services)

**Note**: Free tier services spin down after 15 minutes of inactivity. First request may take 30-60 seconds.

## 📋 Prerequisites

1. GitHub account
2. Render.com account (free - no credit card needed)

## 🎯 Deployment Steps

### Step 1: Push Code to GitHub (if not already done)

```bash
# If you haven't already, push this code to your GitHub
git remote add origin https://github.com/YOUR_USERNAME/wheel-app.git
git push -u origin main
```

### Step 2: Deploy to Render

Choose **ONE** of these methods:

#### Method A: Blueprint (Easiest - Recommended) ⭐

1. **Go to**: https://dashboard.render.com
2. **Sign up/Login** with GitHub
3. **Click**: "New +" → "Blueprint"
4. **Connect**: Your GitHub repository
5. **Select**: The `render.yaml` file (it will be auto-detected)
6. **Click**: "Apply Blueprint"
7. **Wait**: 3-5 minutes for build and deployment

✅ **Done!** Your API will be live at: `https://wheel-analyzer-api.onrender.com`

#### Method B: Manual Setup

1. **Go to**: https://dashboard.render.com
2. **Click**: "New +" → "Web Service"
3. **Connect**: Your GitHub repository
4. **Configure**:
   - **Name**: `wheel-analyzer-api`
   - **Environment**: `Docker`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main` (or your branch name)
   - **Plan**: `Free`
5. **Advanced Settings** (optional):
   - Auto-Deploy: `Yes`
   - Health Check Path: `/health`
6. **Click**: "Create Web Service"
7. **Wait**: 3-5 minutes for deployment

## 🎉 Access Your API

Once deployed, you'll get a URL like: `https://wheel-analyzer-api.onrender.com`

### Test Your API

```bash
# Replace with your actual Render URL
RENDER_URL="https://wheel-analyzer-api.onrender.com"

# Health check
curl $RENDER_URL/health

# Get popular tickers
curl $RENDER_URL/api/v1/popular-tickers

# Analyze AAPL
curl "$RENDER_URL/api/v1/analyze/AAPL?target_dte=30"

# Find best candidates
curl "$RENDER_URL/api/v1/candidates?min_annual_return=20&max_results=5"
```

### Interactive Documentation

Visit these URLs in your browser:

- **Swagger UI**: `https://wheel-analyzer-api.onrender.com/docs`
- **ReDoc**: `https://wheel-analyzer-api.onrender.com/redoc`

## 📱 Example API Calls

### 1. Screen Stocks for Wheel Strategy

```bash
curl -X POST "https://wheel-analyzer-api.onrender.com/api/v1/screen" \
  -H "Content-Type: application/json" \
  -d '{
    "min_market_cap": 10000000000,
    "min_options_volume": 500
  }'
```

### 2. Analyze Specific Ticker

```bash
curl "https://wheel-analyzer-api.onrender.com/api/v1/analyze/TSLA?target_dte=30&delta_min=0.25&delta_max=0.35"
```

### 3. Compare Multiple Tickers

```bash
curl -X POST "https://wheel-analyzer-api.onrender.com/api/v1/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "strategy": "put",
    "target_dte": 30
  }'
```

### 4. Get Best Wheel Candidates

```bash
curl "https://wheel-analyzer-api.onrender.com/api/v1/candidates?min_annual_return=15&max_results=10"
```

## 🔧 Monitoring Your Deployment

### View Logs

1. Go to your Render dashboard
2. Click on your service
3. Click "Logs" tab
4. Watch real-time logs

### Check Health

```bash
curl https://wheel-analyzer-api.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:00:00",
  "version": "1.0.0"
}
```

## ⚙️ Configuration

### Environment Variables (Optional)

In Render dashboard, you can add environment variables:

1. Go to your service
2. Click "Environment" tab
3. Add variables:
   - `LOG_LEVEL`: `INFO` (or `DEBUG` for more logs)
   - `PORT`: `8000` (auto-set by Render)

### Custom Domain (Optional)

1. Go to service settings
2. Click "Custom Domain"
3. Add your domain (free SSL included)

## 🚨 Important Notes

### Free Tier Limitations

- **Spin Down**: Service sleeps after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes 30-60 seconds
- **No Persistent Storage**: Use external database if needed
- **750 Hours/Month**: Enough for testing and light usage

### Keep Your Service Awake (Optional)

Use a free uptime monitor:

**UptimeRobot** (free):
1. Sign up at https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com/health`
   - Interval: 5 minutes
3. Keeps your service warm!

**Cron-job.org** (free):
```bash
# Add a cron job
*/5 * * * * curl https://your-app.onrender.com/health
```

## 🐛 Troubleshooting

### Build Failed

Check logs in Render dashboard. Common issues:
- Missing dependencies in `requirements.txt`
- Dockerfile errors

### Service Not Responding

1. Check health endpoint first: `/health`
2. View logs in Render dashboard
3. Verify environment variables

### 503 Error

Service is spinning up (cold start). Wait 30-60 seconds and try again.

## 🎓 Next Steps

### 1. Test All Endpoints

Visit `https://your-url.onrender.com/docs` and try all endpoints.

### 2. Build a Frontend

Create a simple web interface:
- React/Vue/Svelte frontend
- Call your API from the frontend
- Deploy frontend to Vercel/Netlify (free)

### 3. Add Features

- Implement caching with Redis
- Add user authentication
- Store historical data
- Add email notifications

### 4. Upgrade (Optional)

If you need more power:
- **Starter Plan**: $7/month (no sleep, faster)
- **Standard Plan**: $25/month (more resources)

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [API Documentation](https://your-url.onrender.com/docs)
- [Project GitHub](https://github.com/YOUR_USERNAME/wheel-app)

## 💬 Support

- GitHub Issues: Report bugs or request features
- Render Community: https://community.render.com
- API Docs: Visit `/docs` on your deployed URL

---

## ✅ Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Signed up for Render.com
- [ ] Created web service or applied blueprint
- [ ] Waited for deployment (3-5 minutes)
- [ ] Tested `/health` endpoint
- [ ] Visited `/docs` for interactive API
- [ ] Tested at least one analysis endpoint
- [ ] Set up uptime monitoring (optional)

🎉 **Congratulations!** Your Wheel Strategy Analyzer is now live on the cloud!
