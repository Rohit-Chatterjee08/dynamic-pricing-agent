# 🚀 Production Deployment Guide

This guide provides step-by-step instructions for deploying your Shopify Remix app to production.

## 📋 Pre-Deployment Checklist

### ✅ Code & Dependencies
- [ ] All dependencies are at stable LTS versions
- [ ] No critical security vulnerabilities (`npm audit`)
- [ ] Code passes all linting and type checks
- [ ] All tests are passing
- [ ] Environment variables are properly configured

### ✅ Database
- [ ] Production PostgreSQL database is provisioned
- [ ] Database connection string supports connection pooling
- [ ] Prisma schema is production-ready
- [ ] Migration files are tested and ready
- [ ] Database backup strategy is in place

### ✅ External Services
- [ ] Redis instance is provisioned for sessions and queues
- [ ] Email service is configured (if applicable)
- [ ] Monitoring and logging services are set up

### ✅ Shopify Configuration
- [ ] App is created in Shopify Partner Dashboard
- [ ] App URLs are configured correctly
- [ ] Webhook endpoints are set up
- [ ] Billing configuration is complete (if using Billing API)
- [ ] App is ready for review/publication

## 🏗️ Platform-Specific Deployment

### Option 1: Render.com Deployment

#### 1. Create New Web Service

```bash
# Clone your repository to Render
# Connect your GitHub repository to Render
```

#### 2. Configure Service Settings

| Setting | Value |
|---------|-------|
| **Name** | `shopify-app-production` |
| **Environment** | `Docker` |
| **Build Command** | `docker build -t shopify-app .` |
| **Start Command** | `docker run -p 3000:3000 shopify-app` |
| **Port** | `3000` |

#### 3. Environment Variables

```bash
# Required Environment Variables
SHOPIFY_API_KEY=your_api_key_from_partner_dashboard
SHOPIFY_API_SECRET=your_api_secret_from_partner_dashboard
SHOPIFY_APP_URL=https://your-app-name.onrender.com
SHOPIFY_APP_ENV=production
SCOPES=read_products,write_products,read_orders,read_customers

# Database
DATABASE_URL=postgresql://user:password@host:5432/database?connection_limit=20
DB_CONNECTION_LIMIT=20
DB_POOL_TIMEOUT=10

# Redis
REDIS_URL=redis://user:password@host:6379
REDIS_PREFIX=shopify_app:

# Security
SESSION_SECRET=your_32_character_session_secret
ENCRYPTION_KEY=your_32_character_encryption_key
JWT_SECRET=your_16_character_jwt_secret
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret

# App Configuration
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=info
LOG_FORMAT=json

# Billing
BILLING_MODE=managed  # or 'api'
BILLING_PLAN_NAME=Premium Plan
BILLING_PLAN_PRICE=29.99
BILLING_TRIAL_DAYS=7
```

#### 4. Deploy

```bash
# Render will automatically deploy when you push to main branch
git push origin main
```

### Option 2: Railway Deployment

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

#### 2. Initialize Project

```bash
railway init
railway link
```

#### 3. Add Services

```bash
# Add PostgreSQL
railway add -d postgresql

# Add Redis
railway add -d redis

# Deploy your app
railway up
```

#### 4. Configure Environment Variables

```bash
# Set environment variables
railway vars set SHOPIFY_API_KEY=your_api_key
railway vars set SHOPIFY_API_SECRET=your_api_secret
railway vars set SHOPIFY_APP_URL=https://your-app.up.railway.app
# ... (all other environment variables from above)
```

### Option 3: Vercel Deployment (Serverless)

#### 1. Install Vercel CLI

```bash
npm install -g vercel
vercel login
```

#### 2. Configure Vercel

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "build/server/index.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/build/server/index.js"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

#### 3. Deploy

```bash
# Build for production
npm run build

# Deploy to Vercel
vercel --prod
```

## 🔧 Database Migration

### Run Migrations

```bash
# Connect to your production database
export DATABASE_URL="your_production_database_url"

# Run pending migrations
npx prisma migrate deploy

# Generate Prisma client
npx prisma generate

# Verify migration status
npx prisma migrate status
```

### Backup Before Migration

```bash
# Create database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Or use your cloud provider's backup tool
```

## 🏪 Shopify Partner Dashboard Configuration

### 1. App URLs

| Setting | URL |
|---------|-----|
| **App URL** | `https://your-app.com/` |
| **Allowed redirection URL(s)** | `https://your-app.com/auth/callback` |

### 2. Webhook Configuration

| Topic | URL |
|-------|-----|
| **App uninstalled** | `https://your-app.com/webhooks/app/uninstalled` |
| **Customers data request** | `https://your-app.com/webhooks/customers/data_request` |
| **Customers redact** | `https://your-app.com/webhooks/customers/redact` |
| **Shop redact** | `https://your-app.com/webhooks/shop/redact` |

### 3. App Proxy (if needed)

| Setting | Value |
|---------|-------|
| **Subpath prefix** | `apps` |
| **Subpath** | `your-app-name` |
| **URL** | `https://your-app.com/proxy` |

## 🔒 Security Configuration

### SSL/TLS Certificate

Most hosting platforms (Render, Railway, Vercel) provide automatic HTTPS certificates. Ensure your app is only accessible via HTTPS in production.

### Content Security Policy

The app includes production-ready CSP headers that allow embedding in Shopify admin while maintaining security.

### Rate Limiting

Default rate limiting is set to 100 requests per 15 minutes per IP. Adjust in `lib/security.server.ts` if needed.

## 📊 Monitoring & Alerts

### Health Check Endpoint

Your app includes a health check endpoint at `/healthz` that verifies:

- Database connectivity
- Redis connectivity  
- Basic app functionality

### Log Monitoring

Structured JSON logs are output to stdout. Set up log aggregation with:

- **Render**: Logs available in dashboard
- **Railway**: Built-in logging
- **Vercel**: Vercel Analytics
- **External**: Datadog, New Relic, LogDNA

### Webhook Monitoring

Monitor webhook delivery status in your database:

```sql
-- Check failed webhook deliveries
SELECT topic, shop, status, error_message, created_at 
FROM webhook_deliveries 
WHERE status = 'FAILED' 
ORDER BY created_at DESC;

-- Check webhook processing times
SELECT topic, AVG(EXTRACT(EPOCH FROM (processed_at - created_at)) * 1000) as avg_processing_time_ms
FROM webhook_deliveries 
WHERE status = 'SUCCESS' 
GROUP BY topic;
```

## ✅ Post-Deployment Verification

### Automated Checks

Run the verification script after deployment:

```bash
# Run verification script
npm run verify-deployment
```

### Manual Verification Checklist

#### 1. App Installation Flow

- [ ] Navigate to your app's installation URL
- [ ] Complete OAuth flow successfully
- [ ] App loads properly in Shopify admin
- [ ] No console errors in browser

#### 2. Database Operations

- [ ] New shop record is created on installation
- [ ] Sessions are stored correctly
- [ ] Encrypted fields are properly encrypted

#### 3. Webhook Processing

- [ ] Webhooks are registered automatically after OAuth
- [ ] Test webhook delivery (use ngrok for local testing)
- [ ] HMAC validation is working
- [ ] Webhook processing is queued and executed

#### 4. Billing (if applicable)

- [ ] Subscription creation flow works
- [ ] Billing callbacks are processed
- [ ] Usage recording works (for usage-based billing)

#### 5. Security

- [ ] App only loads over HTTPS
- [ ] CSP headers are present
- [ ] Rate limiting is active
- [ ] No sensitive data in logs

#### 6. Performance

- [ ] App loads within 3 seconds
- [ ] Database queries are optimized
- [ ] Redis connections are working
- [ ] No memory leaks

### Verification Commands

```bash
# Test health endpoint
curl https://your-app.com/healthz

# Check app response time
curl -w "@curl-format.txt" -o /dev/null -s https://your-app.com/

# Verify webhook endpoint
curl -X POST https://your-app.com/webhooks/app/uninstalled \
  -H "X-Shopify-Topic: app/uninstalled" \
  -H "X-Shopify-Shop-Domain: test.myshopify.com" \
  -H "X-Shopify-Hmac-Sha256: test" \
  -d '{}'
```

## 🚨 Rollback Plan

### Quick Rollback

```bash
# Revert to previous deployment
git revert HEAD~1
git push origin main

# Or use platform-specific rollback
# Render: Use dashboard to rollback
# Railway: railway rollback
# Vercel: vercel --prod (previous version)
```

### Database Rollback

```bash
# If you need to rollback database changes
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
```

## 📞 Support & Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **App not loading in Shopify** | Check App URL and allowed redirection URLs |
| **Webhook delivery failures** | Verify HMAC secret and endpoint URLs |
| **Database connection errors** | Check DATABASE_URL and connection limits |
| **Session storage issues** | Verify Redis connectivity and SESSION_SECRET |

### Logs Analysis

```bash
# Check recent errors
grep "ERROR" /var/log/app.log | tail -20

# Monitor webhook failures
grep "webhook_failed" /var/log/app.log

# Check database connection issues
grep "db_connection_error" /var/log/app.log
```

### Performance Monitoring

```bash
# Check response times
grep "http_request" /var/log/app.log | jq '.durationMs' | sort -n

# Monitor memory usage
ps aux | grep node

# Check database query performance
grep "db_query" /var/log/app.log | jq '.durationMs' | sort -n
```

## 🔄 Maintenance

### Regular Tasks

#### Weekly
- [ ] Review application logs for errors
- [ ] Check webhook delivery success rates
- [ ] Monitor database performance
- [ ] Review security alerts

#### Monthly  
- [ ] Update dependencies (`npm audit` and `npm update`)
- [ ] Rotate encryption keys (if policy requires)
- [ ] Review and clean old webhook delivery records
- [ ] Database maintenance and optimization

#### Quarterly
- [ ] Review and update CSP policies
- [ ] Audit user permissions and access
- [ ] Update Shopify API version if needed
- [ ] Performance optimization review

---

## 🎯 Success Metrics

After successful deployment, monitor these key metrics:

- **Uptime**: > 99.9%
- **Response Time**: < 2 seconds average
- **Webhook Success Rate**: > 95%
- **Error Rate**: < 1%
- **Database Query Time**: < 100ms average

Your Shopify app is now production-ready! 🎉
