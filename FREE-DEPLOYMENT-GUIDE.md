# 🆓 Complete FREE Shopify App Deployment Guide

Deploy your production-ready Shopify app for **$0/month** using free tiers. Follow the exact commands below.

---

## 🎯 **What You'll Get (100% FREE)**

- ✅ **Live Shopify app** accessible to merchants
- ✅ **PostgreSQL database** (512MB free)
- ✅ **Redis instance** (25MB free) 
- ✅ **Automatic deployments** via GitHub
- ✅ **HTTPS & custom domain** included
- ✅ **500 hours/month** runtime (always-on)

---

## 🚀 **Option 1: Railway (Recommended - Easiest)**

### **Step 1: Setup Repository**

```powershell
# Navigate to your project
cd D:\Projects\auto_bundler_agent

# Initialize git and push to GitHub
git init
git add .
git commit -m "Production-ready Shopify app"

# Create GitHub repository (do this manually on github.com)
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/shopify-app.git
git branch -M main
git push -u origin main
```

### **Step 2: Generate Secrets**

```powershell
# Generate all required secrets at once
node -e "
const crypto = require('crypto');
console.log('SESSION_SECRET=' + crypto.randomBytes(32).toString('hex'));
console.log('ENCRYPTION_KEY=' + crypto.randomBytes(32).toString('hex'));
console.log('JWT_SECRET=' + crypto.randomBytes(16).toString('hex'));
console.log('SHOPIFY_WEBHOOK_SECRET=' + crypto.randomBytes(32).toString('hex'));
"
```

**Copy the output - you'll need these values!**

### **Step 3: Deploy to Railway**

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway (creates free account)
railway login

# Create new project
railway init
# Choose: "Empty project"
# Project name: "shopify-app"

# Link to your GitHub repo
railway link

# Add PostgreSQL database (FREE)
railway add postgresql

# Add Redis (FREE) 
railway add redis

# Set environment variables (replace with your actual values)
railway variables set SHOPIFY_API_KEY=your_shopify_api_key
railway variables set SHOPIFY_API_SECRET=your_shopify_api_secret
railway variables set SHOPIFY_APP_URL=https://your-app-name.up.railway.app
railway variables set SHOPIFY_APP_ENV=production
railway variables set SCOPES="read_products,write_products,read_orders"
railway variables set SESSION_SECRET=your_generated_session_secret
railway variables set ENCRYPTION_KEY=your_generated_encryption_key
railway variables set JWT_SECRET=your_generated_jwt_secret
railway variables set SHOPIFY_WEBHOOK_SECRET=your_generated_webhook_secret
railway variables set NODE_ENV=production
railway variables set PORT=3000
railway variables set HOST=0.0.0.0
railway variables set LOG_LEVEL=info
railway variables set LOG_FORMAT=json
railway variables set BILLING_MODE=managed
railway variables set DB_CONNECTION_LIMIT=10
railway variables set DB_POOL_TIMEOUT=10
railway variables set REDIS_PREFIX=shopify_app:

# Deploy your app
railway up

# Run database migrations
railway run npx prisma migrate deploy

# Get your app URL
railway status
```

**Your app will be live at:** `https://your-project-name.up.railway.app`

---

## 🚀 **Option 2: Render.com (Alternative FREE)**

### **Step 1: Setup Repository** (same as above)

### **Step 2: Deploy to Render**

```powershell
# No CLI needed - use web interface

# Go to render.com and sign up (free)
# Connect your GitHub account

# Create PostgreSQL Database:
# Dashboard → "New" → "PostgreSQL" 
# Name: shopify-app-db
# Plan: Free (expires in 90 days, then $7/month)

# Create Redis:
# Dashboard → "New" → "Redis"
# Name: shopify-app-redis  
# Plan: Free (25MB)

# Create Web Service:
# Dashboard → "New" → "Web Service"
# Connect repository: your GitHub repo
# Name: shopify-app
# Environment: Docker
# Plan: Free (750 hours/month)
```

**Environment Variables for Render:**
```bash
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_APP_URL=https://your-app-name.onrender.com
DATABASE_URL=$DATABASE_URL  # Auto-provided by Render
REDIS_URL=$REDIS_URL        # Auto-provided by Render
SESSION_SECRET=your_generated_session_secret
ENCRYPTION_KEY=your_generated_encryption_key
JWT_SECRET=your_generated_jwt_secret
SHOPIFY_WEBHOOK_SECRET=your_generated_webhook_secret
NODE_ENV=production
SCOPES=read_products,write_products,read_orders
BILLING_MODE=managed
```

**After deployment, run migrations:**
- Go to Web Service → "Shell"
- Run: `npx prisma migrate deploy`

---

## 🚀 **Option 3: Vercel + Free Database (Serverless)**

### **Step 1: Setup External Database**

**Option 3A: Neon (PostgreSQL - FREE)**

```powershell
# Go to neon.tech and sign up
# Create database: shopify-app
# Copy connection string
```

**Option 3B: Upstash (Redis - FREE)**

```powershell
# Go to upstash.com and sign up  
# Create Redis database
# Copy connection string
```

### **Step 2: Deploy to Vercel**

```powershell
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add SHOPIFY_API_KEY
vercel env add SHOPIFY_API_SECRET
vercel env add DATABASE_URL
vercel env add REDIS_URL
vercel env add SESSION_SECRET
vercel env add ENCRYPTION_KEY
vercel env add JWT_SECRET
vercel env add SHOPIFY_WEBHOOK_SECRET

# Redeploy with environment variables
vercel --prod
```

---

## 🏪 **Shopify Partner Setup (FREE)**

### **Step 1: Create Shopify Partner Account**

```powershell
# Go to partners.shopify.com
# Sign up for free partner account
# No credit card required
```

### **Step 2: Create App**

1. **Partners Dashboard → Apps → Create app**
2. **Choose "Create app manually"**
3. **Fill details:**
   - App name: `Your App Name`
   - App URL: `https://your-deployed-app-url.com`
   - Redirection URLs: `https://your-deployed-app-url.com/auth/callback`

4. **Copy credentials:**
   - API Key → Use in `SHOPIFY_API_KEY`
   - API Secret → Use in `SHOPIFY_API_SECRET`

### **Step 3: Configure Webhooks**

**Add these webhook endpoints:**

| Webhook Topic | URL | Format |
|---------------|-----|---------|
| App uninstalled | `https://your-app-url.com/webhooks/app/uninstalled` | JSON |
| Customer data request | `https://your-app-url.com/webhooks/customers/data_request` | JSON |
| Customer redact | `https://your-app-url.com/webhooks/customers/redact` | JSON |
| Shop redact | `https://your-app-url.com/webhooks/shop/redact` | JSON |

**Webhook secret:** Use your `SHOPIFY_WEBHOOK_SECRET` value

---

## ✅ **Testing Your Free App**

### **Step 1: Verify Health**

```powershell
# Check if app is running
curl https://your-app-url.com/healthz

# Should return JSON with "status": "healthy"
```

### **Step 2: Create Development Store (FREE)**

```powershell
# In Shopify Partners Dashboard:
# Go to "Stores" → "Create store"
# Choose "Development store"
# Store name: test-store
# Password: password123
```

### **Step 3: Install Your App**

```powershell
# Navigate to this URL in browser:
# https://your-app-url.com/api/auth?shop=test-store.myshopify.com
# Complete OAuth flow
# Should redirect to Shopify admin with your app loaded
```

### **Step 4: Test Webhook**

```powershell
# Uninstall and reinstall your app to trigger webhook
# Check your platform logs:

# Railway:
railway logs

# Render:
# Check Dashboard → Logs

# Vercel:
vercel logs
```

---

## 🔍 **Monitoring Your Free App**

### **Check Application Health**

```powershell
# Test health endpoint
curl -H "Accept: application/json" https://your-app-url.com/healthz
```

**Expected Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": { "status": "healthy" },
    "redis": { "status": "healthy" },
    "application": { "status": "healthy" }
  },
  "metrics": {
    "activeShops": 1,
    "totalSessions": 1
  }
}
```

### **Monitor Logs**

```powershell
# Railway
railway logs --tail

# Vercel  
vercel logs --follow

# Render
# Use web dashboard
```

---

## 🆘 **Troubleshooting FREE Deployments**

### **❌ Database Connection Issues**

```powershell
# Railway - Check database status
railway status

# Verify DATABASE_URL format
railway variables
```

### **❌ App Won't Start**

```powershell
# Check environment variables
railway variables

# View real-time logs
railway logs --tail

# Restart service
railway redeploy
```

### **❌ Shopify OAuth Fails**

```powershell
# Verify URLs in Partner Dashboard match deployed app
# Check SHOPIFY_APP_URL environment variable
railway variables get SHOPIFY_APP_URL
```

### **❌ Out of Free Tier Limits**

**Railway Free Limits:**
- 500 hours/month execution
- 1GB RAM
- 1GB storage

**If exceeded:**
```powershell
# Check usage
railway usage

# Optimize by reducing worker processes
# Edit docker-compose.prod.yml - remove worker service
```

---

## 📊 **Free Tier Limits**

### **Railway (Best FREE option)**
- ✅ **PostgreSQL**: 1GB storage
- ✅ **Redis**: 25MB memory  
- ✅ **Runtime**: 500 hours/month
- ✅ **Bandwidth**: 100GB/month
- ✅ **Custom domain**: Included

### **Render**
- ✅ **Web Service**: 750 hours/month
- ✅ **PostgreSQL**: 90 days free, then $7/month
- ✅ **Redis**: 25MB free
- ⚠️ **Note**: Database becomes paid after 90 days

### **Vercel + External DB**
- ✅ **Serverless**: 100GB-hours/month
- ✅ **Neon PostgreSQL**: 512MB free
- ✅ **Upstash Redis**: 10K commands/day free

---

## 🎉 **Success Checklist (100% FREE)**

Your free app is working when:

- [ ] ✅ Health endpoint returns `{"status": "healthy"}`
- [ ] ✅ App installs on development store
- [ ] ✅ Shopify admin loads your app interface
- [ ] ✅ Webhooks are delivered (check logs)
- [ ] ✅ No errors in platform logs
- [ ] ✅ Database stores shop data

---

## 💡 **Pro Tips for Free Hosting**

### **Optimize for Free Tiers**

```powershell
# Reduce memory usage - edit package.json
"scripts": {
  "start": "node --max-old-space-size=256 build/server/index.js"
}

# Disable worker process in production if needed
# Comment out worker service in docker-compose.prod.yml
```

### **Keep Free Apps Alive**

```powershell
# Use uptimerobot.com (free) to ping your app every 5 minutes
# Monitor: https://your-app-url.com/healthz
# Prevents free tier from sleeping
```

### **Monitor Usage**

```powershell
# Railway - check usage
railway usage

# Set up alerts before hitting limits
railway notifications
```

---

## 🚀 **Going Live With Your FREE App**

### **For Personal/Testing Use**
- Your free app is ready to use!
- Share installation URL: `https://your-app-url.com/api/auth?shop=STORE.myshopify.com`

### **For Client Projects** 
- Free tiers work great for small merchants
- Can handle 10-50 stores easily
- Upgrade to paid plans when you grow

### **Scaling Beyond Free**
- **Railway**: $5/month removes limits
- **Render**: $7/month for guaranteed database  
- **Vercel**: $20/month for team features

---

## 🏆 **Congratulations!**

You now have a **completely FREE, production-ready Shopify app** running at:
- `https://your-app-name.up.railway.app` (Railway)
- `https://your-app-name.onrender.com` (Render)  
- `https://your-app-name.vercel.app` (Vercel)

**Your FREE app includes:**
- ✅ Multi-tenant PostgreSQL database
- ✅ Redis session storage & job queues
- ✅ Enterprise-grade security
- ✅ Webhook processing
- ✅ Health monitoring
- ✅ Automatic deployments

**Total Monthly Cost: $0** 💸

Start building your Shopify app empire for free! 🚀
