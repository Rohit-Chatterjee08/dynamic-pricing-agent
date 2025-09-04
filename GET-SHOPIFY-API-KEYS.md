# 🔑 How to Get Your Shopify API Keys (FREE)

You need Shopify API keys before deploying your app. Here's exactly how to get them for **FREE**.

---

## 🏪 **Step 1: Create Shopify Partner Account (FREE)**

### **Go to Shopify Partners**
```
https://partners.shopify.com
```

### **Sign Up Process**
1. **Click "Join now"**
2. **Fill in your details:**
   - First Name: `Your Name`
   - Last Name: `Your Last Name`
   - Email: `your-email@gmail.com`
   - Country: `Your Country`
   
3. **Click "Create account"**
4. **Verify your email** (check inbox)
5. **Complete profile setup** (business details - can be personal)

**✅ No credit card required - completely FREE!**

---

## 📱 **Step 2: Create Your Shopify App**

### **Navigate to Apps Section**
1. **Login to** [partners.shopify.com](https://partners.shopify.com)
2. **Click "Apps"** in the left sidebar
3. **Click "Create app"** button

### **Choose App Type**
1. **Select "Create app manually"** (not CLI)
2. **Click "Continue"**

### **Fill App Details**

**Basic Information:**
- **App name**: `Your App Name` (e.g., "My Shopify App")
- **App handle**: `your-app-name` (auto-generated, you can edit)

**App URLs (use placeholder for now):**
- **App URL**: `https://temporary-url.com`
- **Allowed redirection URLs**: `https://temporary-url.com/auth/callback`

**Note**: You'll update these URLs after deployment!

### **Click "Create app"**

---

## 🔐 **Step 3: Get Your API Keys**

### **After App Creation:**

1. **You'll be redirected to your app dashboard**
2. **Look for "Client credentials" section**
3. **You'll see two important values:**

```
Client ID: abcd1234567890abcdef
Client secret: shpcs_1234567890abcdef1234567890abcdef
```

### **Copy These Values:**

```bash
SHOPIFY_API_KEY=abcd1234567890abcdef
SHOPIFY_API_SECRET=shpcs_1234567890abcdef1234567890abcdef
```

**🔒 Keep your Client Secret secure - treat it like a password!**

---

## ⚙️ **Step 4: Configure App Permissions**

### **Set App Scopes**
1. **Go to "App setup" tab**
2. **Scroll to "App permissions"**
3. **Check these permissions:**
   - ✅ `read_products` - Read product data
   - ✅ `write_products` - Modify products (optional)
   - ✅ `read_orders` - Read order data (optional)
   - ✅ `read_customers` - Read customer data (optional)

4. **Click "Save"**

### **Your SCOPES value:**
```bash
SCOPES=read_products,write_products,read_orders,read_customers
```

---

## 🔗 **Step 5: Update URLs After Deployment**

**After you deploy your app, you'll come back and update:**

### **For Railway deployment:**
- **App URL**: `https://your-app-name.up.railway.app`
- **Redirection URL**: `https://your-app-name.up.railway.app/auth/callback`

### **For Render deployment:**
- **App URL**: `https://your-app-name.onrender.com`
- **Redirection URL**: `https://your-app-name.onrender.com/auth/callback`

### **For Vercel deployment:**
- **App URL**: `https://your-app-name.vercel.app`
- **Redirection URL**: `https://your-app-name.vercel.app/auth/callback`

---

## 🎯 **Complete Environment Variables**

**After getting your API keys, you'll have:**

```bash
# From Shopify Partner Dashboard
SHOPIFY_API_KEY=your_client_id_here
SHOPIFY_API_SECRET=your_client_secret_here
SHOPIFY_APP_URL=https://your-deployed-app-url.com
SCOPES=read_products,write_products,read_orders

# Generated secrets (from previous guide)
SESSION_SECRET=your_generated_session_secret
ENCRYPTION_KEY=your_generated_encryption_key
JWT_SECRET=your_generated_jwt_secret
SHOPIFY_WEBHOOK_SECRET=your_generated_webhook_secret

# App configuration
NODE_ENV=production
SHOPIFY_APP_ENV=production
BILLING_MODE=managed
```

---

## 🧪 **Step 6: Create Development Store (FREE)**

### **For Testing Your App:**

1. **Go to "Stores" in Partner Dashboard**
2. **Click "Create store"**
3. **Choose "Development store"**
4. **Fill details:**
   - Store name: `test-store`
   - Store URL: `test-store` (becomes test-store.myshopify.com)
   - Password: `password123`
   - Purpose: `Testing my app`

5. **Click "Create store"**

**✅ Development stores are FREE and perfect for testing!**

---

## 🔍 **Step 7: Test Your API Keys**

### **Quick Test (after deployment):**

```bash
# Test installation URL
https://your-deployed-app.com/api/auth?shop=test-store.myshopify.com
```

**Expected flow:**
1. Redirects to Shopify OAuth screen
2. Shows your app name and requested permissions
3. Click "Install app"
4. Redirects back to your app
5. App loads in Shopify admin

---

## 📋 **API Keys Checklist**

Before deploying, make sure you have:

- [ ] ✅ Shopify Partner account created (FREE)
- [ ] ✅ App created in Partner Dashboard
- [ ] ✅ `SHOPIFY_API_KEY` (Client ID) copied
- [ ] ✅ `SHOPIFY_API_SECRET` (Client Secret) copied
- [ ] ✅ App permissions/scopes configured
- [ ] ✅ Development store created for testing
- [ ] ✅ All environment variables ready

---

## 🚨 **Common Issues & Solutions**

### **❌ "Invalid API key" error**
**Problem**: Wrong API key format
**Solution**: 
- API key should be ~20 characters: `abcd1234567890abcdef`
- Not the app handle or name

### **❌ "Invalid client secret" error**
**Problem**: Wrong secret format  
**Solution**:
- Client secret starts with `shpcs_`: `shpcs_1234567890abcdef...`
- Copy the full secret (usually 50+ characters)

### **❌ "App URL mismatch" error**
**Problem**: URLs in Partner Dashboard don't match deployed app
**Solution**:
1. Deploy your app first
2. Get the live URL (e.g., `https://your-app.up.railway.app`)
3. Update URLs in Partner Dashboard → App setup

### **❌ "Scope mismatch" error**
**Problem**: App requests different permissions than configured
**Solution**:
- Check SCOPES environment variable matches Partner Dashboard
- Common scopes: `read_products,write_products,read_orders`

---

## 🎉 **You're Ready!**

Once you have your API keys, you can:

1. **Follow the FREE deployment guide**
2. **Set your environment variables**
3. **Deploy your app**
4. **Update URLs in Partner Dashboard**
5. **Test installation on development store**

Your Shopify API keys are **FREE forever** - no subscription or usage fees! 🆓

---

## 💡 **Pro Tips**

### **Keep API Keys Secure**
- Never commit API keys to GitHub
- Use environment variables only
- Regenerate if accidentally exposed

### **Development vs Production**
- Use same API keys for both environments
- Change `SHOPIFY_APP_URL` between dev/prod
- Keep separate development stores for testing

### **App Store Submission**
- Same API keys work for App Store apps
- No additional keys needed for public apps
- Can handle unlimited installations

**Ready to deploy? Go back to the FREE deployment guide and use your new API keys!** 🚀
