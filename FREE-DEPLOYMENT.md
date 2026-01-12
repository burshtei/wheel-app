# 🎉 FREE Cloud Deployment Guide

Deploy your Wheel Strategy Analyzer to the cloud **completely FREE**! This guide covers platforms that offer generous free tiers with no credit card required (or credits you won't use up).

## 🌟 Best Free Options (Ranked)

### 1. ⭐ Render.com (Easiest - RECOMMENDED)

**Free Tier:**
- 750 hours/month free (enough for 24/7 operation)
- 512 MB RAM
- Shared CPU
- Auto-sleep after 15 mins of inactivity
- Wake up on request (~30 second cold start)

**Deployment Steps:**

#### Option A: Via Dashboard (Easiest)
1. Create account at [https://render.com](https://render.com) (no credit card needed)
2. Fork or push this repo to your GitHub
3. In Render Dashboard:
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select `burshtei/wheel-app`
   - Click **"Apply"**
4. Done! Your app will be at: `https://wheel-analyzer.onrender.com`

#### Option B: Using render.yaml (Automatic)
The repository already includes `render.yaml`. Just connect the repo and Render auto-configures everything!

**Pros:**
- ✅ Zero configuration needed
- ✅ Automatic HTTPS
- ✅ Easy to use dashboard
- ✅ GitHub integration with auto-deploys
- ✅ Free custom domains

**Cons:**
- ⚠️ Cold starts after 15 mins of inactivity
- ⚠️ Limited to 512 MB RAM

---

### 2. ⭐ Fly.io (Best Performance)

**Free Tier:**
- 3 shared-cpu-1x VMs with 256MB RAM each
- 160GB outbound data transfer
- Auto-stop when idle (true serverless)
- Fast cold starts (~2-5 seconds)

**Deployment Steps:**

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login (creates account if needed):
```bash
flyctl auth login
```

3. Launch your app:
```bash
flyctl launch --config fly.toml
```

4. Deploy:
```bash
flyctl deploy
```

**Your app will be at:** `https://wheel-analyzer.fly.dev`

**Useful Commands:**
```bash
flyctl status          # Check app status
flyctl logs            # View logs
flyctl open            # Open in browser
flyctl scale count 1   # Ensure 1 instance always running
```

**Or use the helper script:**
```bash
chmod +x deploy/free-cloud-deploy.sh
./deploy/free-cloud-deploy.sh
# Choose option 2
```

**Pros:**
- ✅ Better performance than Render
- ✅ Multiple regions available
- ✅ Fast cold starts
- ✅ True serverless (pay only when running)

**Cons:**
- ⚠️ Requires CLI tool installation
- ⚠️ Credit card required (but won't be charged on free tier)

---

### 3. ⭐ Railway.app

**Free Tier:**
- $5 free credits per month
- ~500 hours of runtime
- 512 MB RAM
- 1 GB disk
- Executes builds in GitHub Actions

**Deployment Steps:**

1. Create account at [https://railway.app](https://railway.app)
2. Connect your GitHub account
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select this repository: `burshtei/wheel-app`
5. Railway auto-detects the Dockerfile
6. Click **"Generate Domain"** to get public URL

**Your app will be at:** `https://wheel-analyzer.up.railway.app`

**Pros:**
- ✅ Very generous free tier
- ✅ No cold starts
- ✅ Beautiful dashboard
- ✅ Automatic deploys from GitHub

**Cons:**
- ⚠️ Free credits run out after ~500 hours
- ⚠️ Need to monitor usage

---

## 🎯 Quick Comparison

| Platform | Setup Time | Cold Starts | RAM | Best For |
|----------|-----------|-------------|-----|----------|
| **Render** | 2 mins | Yes (30s) | 512MB | Beginners, prototypes |
| **Fly.io** | 5 mins | Yes (2-5s) | 256MB | Performance, production |
| **Railway** | 2 mins | No | 512MB | Always-on apps |

---

## 🚀 Super Quick Start

### Absolute Fastest (Render.com):

1. **Push this code to GitHub** (already done ✓)
2. **Go to [render.com](https://render.com)** → Sign up
3. **Click "New +" → "Blueprint"**
4. **Select your repo** → Click "Apply"
5. **Done!** Access your API at the provided URL

### Alternative: Use the Helper Script

```bash
chmod +x deploy/free-cloud-deploy.sh
./deploy/free-cloud-deploy.sh
```

Follow the prompts to deploy to your chosen platform!

---

## 📡 Testing Your Deployed API

Once deployed, test your API:

```bash
# Replace YOUR-APP-URL with your actual URL
export API_URL="https://wheel-analyzer.onrender.com"

# Health check
curl $API_URL/health

# Analyze a stock
curl "$API_URL/analyze/AAPL"

# Get put opportunities
curl "$API_URL/ticker/TSLA/puts?target_dte=30"

# Screen stocks
curl -X POST $API_URL/screen \
  -H "Content-Type: application/json" \
  -d '{
    "min_market_cap": 10000000000,
    "min_iv_rank": 30
  }'
```

---

## 🎨 Access API Documentation

All platforms provide automatic API documentation:

- **Swagger UI**: `https://your-app-url/docs`
- **ReDoc**: `https://your-app-url/redoc`

---

## 💡 Tips for Free Tiers

### Render.com Tips:
- **Keep-alive service**: Use a free cron service like [cron-job.org](https://cron-job.org) to ping your app every 14 minutes to prevent sleep
- **Health check**: Set up monitoring at [UptimeRobot](https://uptimerobot.com) (also free)

### Fly.io Tips:
- **Auto-stop**: The free tier auto-stops when idle (saves your free allowance)
- **Scale down**: Use `flyctl scale count 1` to ensure only 1 instance runs
- **Monitor usage**: Check with `flyctl status` and `flyctl dashboard`

### Railway Tips:
- **Monitor credits**: Check usage at [railway.app/account/usage](https://railway.app/account/usage)
- **Optimize costs**: Free tier gives you ~500 hours/month, perfect for part-time use

---

## 🔄 Automatic Deployments

All platforms support automatic deployments when you push to GitHub:

### Render:
- Automatically deploys on every push to main branch
- Configure in: **Dashboard → Service → Settings → Build & Deploy**

### Fly.io:
- Set up GitHub Actions:
```yaml
# Add to .github/workflows/fly-deploy.yml
name: Fly Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### Railway:
- Automatically deploys on every push
- No configuration needed!

---

## 🛠️ Troubleshooting

### App shows "Application failed to respond"
- Check logs in your platform dashboard
- Verify port 8080 is being used (configured in Dockerfile)
- Wait for initial build to complete (2-5 minutes)

### Cold start takes too long (Render)
- This is normal for free tier (15-30 seconds)
- Consider using a keep-alive service or upgrade to paid tier

### Build fails
- Check that all files are committed and pushed to GitHub
- Verify `requirements.txt` has all dependencies
- Check build logs in platform dashboard

### API returns errors
- Check application logs
- Verify the app can access external APIs (yfinance)
- Test locally first with `docker-compose up`

---

## 📊 Expected Performance

### Cold Start Times:
- **Render**: 15-30 seconds
- **Fly.io**: 2-5 seconds
- **Railway**: N/A (no cold starts on free tier)

### Response Times (after warm-up):
- **Health check**: < 100ms
- **Analyze ticker**: 2-5 seconds (depends on market data API)
- **Screen stocks**: 10-30 seconds (multiple API calls)

---

## 🎓 Next Steps After Deployment

1. **Set up monitoring**: Use [UptimeRobot](https://uptimerobot.com) for free uptime monitoring
2. **Custom domain**: All platforms support free custom domains
3. **API authentication**: Add authentication for production use
4. **Rate limiting**: Implement rate limiting to prevent abuse
5. **Caching**: Add Redis (available on paid tiers) for better performance

---

## 💰 Cost to Scale Up

If you outgrow the free tier:

| Platform | Starter Plan | Features |
|----------|-------------|----------|
| **Render** | $7/month | No cold starts, more RAM |
| **Fly.io** | Pay-as-you-go | ~$2-5/month for small app |
| **Railway** | $5/month | 5$ credit, ~$10 total resources |

---

## ✅ My Recommendation

**For absolute beginners:** Start with **Render.com**
- Click a few buttons and you're done
- No CLI tools needed
- Great documentation

**For developers:** Use **Fly.io**
- Better performance
- More control
- Modern serverless architecture

**For always-on apps:** Try **Railway.app**
- No cold starts
- Beautiful dashboard
- Easy monitoring

---

## 🆘 Need Help?

- **Render Support**: [https://render.com/docs](https://render.com/docs)
- **Fly.io Support**: [https://fly.io/docs](https://fly.io/docs)
- **Railway Support**: [https://docs.railway.app](https://docs.railway.app)

Happy deploying! 🚀
