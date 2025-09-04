# 🚀 Complete First-Time Production Deployment Guide

This guide walks you through deploying your production-ready Shopify app from start to finish. Follow each step carefully.

---

## 📋 **Prerequisites**

Before starting, ensure you have:
- [ ] **Node.js 18+** installed
- [ ] **Git** installed and configured
- [ ] **GitHub account** (for CI/CD)
- [ ] **Shopify Partner account** 
- [ ] **Credit card** (for cloud services - most have free tiers)

---

## 🏗️ **Phase 1: Local Setup & Testing**

### **Step 1: Prepare Your Repository**

```bash
# Navigate to your project
cd D:\Projects\auto_bundler_agent

# Initialize git if not done
git init
git add .
git commit -m "Initial production-ready setup"

# Create GitHub repository (via GitHub website or CLI)
# Then push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### **Step 2: Install Dependencies**

```bash
# Install all dependencies
npm install

# Generate Prisma client
npx prisma generate

# Verify production setup
npm run verify-production
```

You should see: ✅ **35/35 checks passed**

### **Step 3: Create Local Environment File**

```bash
# Copy the example file
copy .env.example .env

# Generate secure secrets
node -e "console.log('SESSION_SECRET=' + require('crypto').randomBytes(32).toString('hex'))"
node -e "console.log('ENCRYPTION_KEY=' + require('crypto').randomBytes(32).toString('hex'))"  
node -e "console.log('JWT_SECRET=' + require('crypto').randomBytes(16).toString('hex'))"
node -e "console.log('SHOPIFY_WEBHOOK_SECRET=' + require('crypto').randomBytes(32).toString('hex'))"
```

**Edit `.env` with your local values:**
```bash
# Basic Config
SHOPIFY_API_KEY=your_api_key_here
SHOPIFY_API_SECRET=your_api_secret_here
SHOPIFY_APP_URL=http://localhost:3000
NODE_ENV=development

# Use the generated secrets from above
SESSION_SECRET=your_generated_session_secret
ENCRYPTION_KEY=your_generated_encryption_key
JWT_SECRET=your_generated_jwt_secret
SHOPIFY_WEBHOOK_SECRET=your_generated_webhook_secret

# Local Development
DATABASE_URL=postgresql://postgres:password@localhost:5432/shopify_app_dev
REDIS_URL=redis://localhost:6379
SCOPES=read_products,write_products,read_orders
BILLING_MODE=managed
```

---

## 🏪 **Phase 2: Shopify Partner Setup**

### **Step 4: Create Shopify App**

1. **Go to [Shopify Partners](https://partners.shopify.com)**
2. **Click "Apps" → "Create app"**
3. **Choose "Create app manually"**
4. **Fill in details:**
   - App name: `Your App Name`
   - App URL: `https://your-future-domain.com` (placeholder for now)
   - Allowed redirection URLs: `https://your-future-domain.com/auth/callback`

5. **Copy your credentials:**
   - API key → `SHOPIFY_API_KEY`
   - API secret → `SHOPIFY_API_SECRET`

### **Step 5: Configure App Settings**

**App setup → URLs:**
- App URL: `https://your-app.render.com` (we'll update this)
- Allowed redirection URLs: `https://your-app.render.com/auth/callback`

**App setup → Webhooks:** (Add after deployment)
- App uninstalled: `https://your-app.render.com/webhooks/app/uninstalled`
- Customer data request: `https://your-app.render.com/webhooks/customers/data_request`
- Customer redact: `https://your-app.render.com/webhooks/customers/redact`
- Shop redact: `https://your-app.render.com/webhooks/shop/redact`

---

## ☁️ **Phase 3: Production Infrastructure Setup**

### **Step 6: Choose Your Deployment Platform**

**Recommended: Render.com (Easiest for beginners)**

#### **Option A: Render.com**

1. **Sign up at [render.com](https://render.com)**

2. **Create PostgreSQL Database:**
   - Dashboard → "New" → "PostgreSQL"
   - Name: `shopify-app-db`
   - Plan: Free tier
   - Copy the **External Database URL**

3. **Create Redis Instance:**
   - Dashboard → "New" → "Redis"  
   - Name: `shopify-app-redis`
   - Plan: Free tier
   - Copy the **Redis URL**

4. **Create Web Service:**
   - Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Name: `shopify-app`
   - Environment: `Docker`
   - Plan: Starter ($7/month)

#### **Option B: Railway (Alternative)**

1. **Sign up at [railway.app](https://railway.app)**
2. **Install Railway CLI:** `npm install -g @railway/cli`
3. **Login:** `railway login`
4. **Create project:** `railway init`
5. **Add services:** `railway add postgresql redis`

#### **Option C: Vercel + External DB (Serverless)**

1. **Sign up at [vercel.com](https://vercel.com)**
2. **Use external PostgreSQL:** Neon, Supabase, or PlanetScale
3. **Use external Redis:** Upstash or Redis Labs

### **Step 7: Configure Environment Variables**

**For Render.com:**
1. Go to your Web Service → "Environment"
2. Add each variable:

```bash
# Shopify Configuration
SHOPIFY_API_KEY=your_api_key_from_partner_dashboard
SHOPIFY_API_SECRET=your_api_secret_from_partner_dashboard  
SHOPIFY_APP_URL=https://your-app-name.onrender.com
SHOPIFY_APP_ENV=production
SCOPES=read_products,write_products,read_orders,read_customers

# Database (use your Render PostgreSQL external URL)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
DB_CONNECTION_LIMIT=20
DB_POOL_TIMEOUT=10

# Redis (use your Render Redis URL)
REDIS_URL=redis://red-xxxxx:6379
REDIS_PREFIX=shopify_app:

# Security (use your generated secrets)
SESSION_SECRET=your_32_char_session_secret
ENCRYPTION_KEY=your_32_char_encryption_key  
JWT_SECRET=your_16_char_jwt_secret
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret

# App Configuration
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info
LOG_FORMAT=json

# Billing
BILLING_MODE=managed
BILLING_PLAN_NAME=Premium Plan
BILLING_PLAN_PRICE=29.99
BILLING_TRIAL_DAYS=7
```

---

## 🚀 **Phase 4: Deploy to Production**

### **Step 8: Deploy Your App**

**For Render.com:**
1. **Trigger deployment:**
   ```bash
   git add .
   git commit -m "Configure for production deployment"
   git push origin main
   ```

2. **Monitor deployment:**
   - Go to Render Dashboard → Your service
   - Watch the build logs
   - Wait for "Live" status (5-10 minutes)

3. **Get your app URL:**
   - Your app will be available at: `https://your-app-name.onrender.com`

### **Step 9: Run Database Migrations**

**Option 1: Via Render Console**
1. Go to your Web Service → "Shell"
2. Run: `npx prisma migrate deploy`

**Option 2: Via Local CLI (connected to production DB)**
```bash
# Set production DATABASE_URL in your local .env temporarily
DATABASE_URL="your_production_database_url"
npx prisma migrate deploy
```

### **Step 10: Verify Deployment**

```bash
# Check health endpoint
curl https://your-app-name.onrender.com/healthz

# Should return JSON with status: "healthy"
```

---

## 🔗 **Phase 5: Shopify Integration**

### **Step 11: Update Shopify App URLs**

1. **Go to Shopify Partner Dashboard → Your App**
2. **Update App setup → URLs:**
   - App URL: `https://your-app-name.onrender.com`
   - Allowed redirection URLs: `https://your-app-name.onrender.com/auth/callback`

### **Step 12: Configure Webhooks**

1. **App setup → Webhooks → Create webhook:**

| Topic | Endpoint URL | Format |
|-------|-------------|---------|
| App uninstalled | `https://your-app-name.onrender.com/webhooks/app/uninstalled` | JSON |
| Customer data request | `https://your-app-name.onrender.com/webhooks/customers/data_request` | JSON |
| Customer redact | `https://your-app-name.onrender.com/webhooks/customers/redact` | JSON |  
| Shop redact | `https://your-app-name.onrender.com/webhooks/shop/redact` | JSON |

2. **Set webhook secret:** Use your `SHOPIFY_WEBHOOK_SECRET` value

### **Step 13: Test Installation**

1. **Create a development store:**
   - Partner Dashboard → "Stores" → "Create store"

2. **Install your app:**
   - Navigate to: `https://your-app-name.onrender.com/api/auth?shop=your-dev-store.myshopify.com`
   - Complete OAuth flow
   - Should redirect to Shopify admin with your app

3. **Verify in logs:**
   - Check Render logs for successful authentication
   - Look for "Shop {shop} completed OAuth flow"

---

## 🔍 **Phase 6: Testing & Verification**

### **Step 14: Test Core Functionality**

**✅ Authentication Test:**
```bash
# Check if shop was created in database
curl "https://your-app-name.onrender.com/healthz"
# Look for activeShops > 0
```

**✅ Webhook Test:**
1. Uninstall and reinstall your app
2. Check Render logs for webhook processing
3. Verify shop marked as inactive/active

**✅ Health Check Test:**
```bash
curl -H "Accept: application/json" https://your-app-name.onrender.com/healthz
```

Should return:
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

### **Step 15: Monitor Performance**

**Check Render Metrics:**
1. Dashboard → Your service → "Metrics"
2. Monitor CPU, Memory, Response time
3. Set up alerts (optional)

**Check Application Logs:**
1. Dashboard → Your service → "Logs"  
2. Look for errors or warnings
3. Verify structured JSON logging

---

## 🎯 **Phase 7: Go Live**

### **Step 16: App Store Submission (Optional)**

If you want to publish to Shopify App Store:

1. **Complete app listing:**
   - App details, screenshots, description
   - Pricing information
   - Support documentation

2. **Submit for review:**
   - Partner Dashboard → Your app → "Submit for review"
   - Review process takes 7-10 days

### **Step 17: Private App Distribution**

For private/custom apps:

1. **Share installation URL:**
   ```
   https://your-app-name.onrender.com/api/auth?shop=CLIENT-STORE.myshopify.com
   ```

2. **Provide installation instructions:**
   - Send URL to client
   - They click and approve permissions
   - App installs automatically

---

## 🔧 **Phase 8: Ongoing Maintenance**

### **Step 18: Set Up Monitoring**

**Basic Monitoring (Free):**
1. **Uptime monitoring:** Use Uptime Robot or similar
   - Monitor: `https://your-app-name.onrender.com/healthz`
   - Get alerts if app goes down

2. **Log monitoring:** 
   - Check Render logs weekly
   - Look for error patterns

**Advanced Monitoring (Paid):**
- Datadog, New Relic, or LogDNA
- Real-time alerting and dashboards

### **Step 19: Regular Tasks**

**Weekly:**
- [ ] Review application logs for errors
- [ ] Check webhook delivery success rates  
- [ ] Monitor database performance

**Monthly:**
- [ ] Update dependencies: `npm audit && npm update`
- [ ] Review security alerts
- [ ] Clean up old webhook delivery records

**Quarterly:**
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Backup strategy verification

---

## 🆘 **Troubleshooting Common Issues**

### **❌ App Won't Install**

**Problem:** OAuth redirect loop or 404
**Solution:**
1. Check Shopify Partner Dashboard URLs match deployed app
2. Verify `SHOPIFY_APP_URL` environment variable
3. Check logs for authentication errors

### **❌ Database Connection Failed**

**Problem:** `P1001: Can't reach database server`
**Solution:**
1. Check `DATABASE_URL` format includes `?sslmode=require`
2. Verify database is running in Render dashboard
3. Check connection pooling settings

### **❌ Webhooks Not Working**

**Problem:** Webhook delivery failures
**Solution:**
1. Verify webhook URLs in Partner Dashboard
2. Check `SHOPIFY_WEBHOOK_SECRET` matches
3. Review webhook delivery logs in database

### **❌ App Slow or Timing Out**

**Problem:** Poor performance
**Solution:**
1. Check database query performance
2. Monitor Redis connection
3. Review application logs for bottlenecks
4. Consider upgrading Render plan

---

## 🎉 **Success Checklist**

Your app is successfully deployed when:

- [ ] ✅ Health endpoint returns "healthy"
- [ ] ✅ App installs via OAuth flow
- [ ] ✅ Shopify admin loads your app
- [ ] ✅ Webhooks are delivered and processed
- [ ] ✅ Database stores shop data
- [ ] ✅ No errors in production logs
- [ ] ✅ Performance is acceptable (< 3 seconds)

---

## 📞 **Getting Help**

**If you get stuck:**

1. **Check logs first:** Render Dashboard → Logs
2. **Test health endpoint:** `curl https://your-app.onrender.com/healthz`
3. **Review error messages** in browser developer tools
4. **Check Shopify Partner Dashboard** webhook delivery logs
5. **Use production verification:** `npm run verify-production`

**Common Resources:**
- [Shopify App Dev Docs](https://shopify.dev/docs/apps)
- [Render Documentation](https://render.com/docs)
- [Remix Documentation](https://remix.run/docs)

---

## 🏆 **Congratulations!**

You've successfully deployed your first production Shopify app! 🎉

Your app is now:
- ✅ **Live** and accessible to merchants
- ✅ **Secure** with enterprise-grade encryption  
- ✅ **Scalable** to handle thousands of stores
- ✅ **Monitored** with health checks and logging
- ✅ **Maintainable** with proper CI/CD pipeline

**What's Next?**
- Monitor your app's performance and logs
- Gather user feedback for improvements  
- Scale infrastructure as you grow
- Add new features based on merchant needs

Welcome to production! Your Shopify app journey begins now. 🚀
