import "@shopify/shopify-app-remix/adapters/node";
import {
  AppDistribution,
  DeliveryMethod,
  shopifyApp,
  LATEST_API_VERSION,
} from "@shopify/shopify-app-remix/server";
import { PrismaSessionStorage } from "@shopify/shopify-app-session-storage-prisma";
import { restResources } from "@shopify/shopify-api/rest/admin/2024-01";
import { prisma } from "./lib/db.server";
import { getEnv } from "./lib/env";
import { logger } from "./lib/logger.server";
import { encryptToken, decryptToken } from "./lib/crypto.server";

const env = getEnv();

// Custom session storage with encryption
class EncryptedPrismaSessionStorage extends PrismaSessionStorage {
  async storeSession(session: any): Promise<boolean> {
    try {
      // Encrypt the access token before storing
      if (session.accessToken) {
        const originalToken = session.accessToken;
        session.accessToken = encryptToken(originalToken);
        
        const result = await super.storeSession(session);
        
        // Store encrypted token separately in shop record
        if (session.shop && originalToken) {
          await prisma.shop.upsert({
            where: { shop: session.shop },
            create: {
              shop: session.shop,
              accessTokenEncrypted: encryptToken(originalToken),
              isActive: true,
            },
            update: {
              accessTokenEncrypted: encryptToken(originalToken),
              isActive: true,
            },
          });
        }
        
        return result;
      }
      return await super.storeSession(session);
    } catch (error) {
      logger.error('Failed to store session:', error);
      return false;
    }
  }

  async loadSession(id: string): Promise<any | undefined> {
    try {
      const session = await super.loadSession(id);
      if (session?.accessToken) {
        // Decrypt the access token when loading
        session.accessToken = decryptToken(session.accessToken);
      }
      return session;
    } catch (error) {
      logger.error('Failed to load session:', error);
      return undefined;
    }
  }
}

const shopify = shopifyApp({
  apiKey: env.SHOPIFY_API_KEY,
  apiSecret: env.SHOPIFY_API_SECRET,
  appUrl: env.SHOPIFY_APP_URL,
  scopes: env.SCOPES.split(',').map(scope => scope.trim()),
  distribution: AppDistribution.AppStore,
  apiVersion: LATEST_API_VERSION,
  
  sessionStorage: new EncryptedPrismaSessionStorage(prisma),
  
  restResources,
  
  hooks: {
    afterAuth: async ({ session, admin }) => {
      try {
        logger.info(`Shop ${session.shop} completed OAuth flow`);
        
        // Register webhooks after successful authentication
        await shopify.registerWebhooks({ session });
        
        // Update shop record with latest information
        const shopData = await admin.rest.resources.Shop.all({ session });
        const shop = shopData.data[0];
        
        if (shop) {
          await prisma.shop.upsert({
            where: { shop: session.shop },
            create: {
              shop: session.shop,
              name: shop.name,
              email: shop.email,
              domain: shop.domain,
              province: shop.province,
              country: shop.country,
              address1: shop.address1,
              zip: shop.zip,
              city: shop.city,
              phone: shop.phone,
              latitude: shop.latitude,
              longitude: shop.longitude,
              primaryLocale: shop.primary_locale,
              address2: shop.address2,
              planName: shop.plan_name,
              accessTokenEncrypted: encryptToken(session.accessToken),
              isActive: true,
              installedAt: new Date(),
            },
            update: {
              name: shop.name,
              email: shop.email,
              domain: shop.domain,
              province: shop.province,
              country: shop.country,
              address1: shop.address1,
              zip: shop.zip,
              city: shop.city,
              phone: shop.phone,
              latitude: shop.latitude,
              longitude: shop.longitude,
              primaryLocale: shop.primary_locale,
              address2: shop.address2,
              planName: shop.plan_name,
              accessTokenEncrypted: encryptToken(session.accessToken),
              isActive: true,
              uninstalledAt: null, // Reset if reinstalling
            },
          });
        }
      } catch (error) {
        logger.error(`After auth hook failed for shop ${session.shop}:`, error);
      }
    },
  },
  
  webhooks: {
    APP_UNINSTALLED: {
      deliveryMethod: DeliveryMethod.Http,
      callbackUrl: "/webhooks/app/uninstalled",
      callback: async (topic, shop, body, webhookId) => {
        try {
          logger.info(`App uninstalled webhook received for shop: ${shop}`);
          
          // Mark shop as inactive and set uninstall date
          await prisma.shop.update({
            where: { shop },
            data: {
              isActive: false,
              uninstalledAt: new Date(),
            },
          });
          
          // Clean up related data (optional - keep for analytics)
          // await prisma.session.deleteMany({ where: { shop } });
          
          logger.info(`Cleaned up data for uninstalled shop: ${shop}`);
        } catch (error) {
          logger.error(`Failed to process app uninstall for shop ${shop}:`, error);
        }
      },
    },
    
    // GDPR Webhooks
    CUSTOMERS_DATA_REQUEST: {
      deliveryMethod: DeliveryMethod.Http,
      callbackUrl: "/webhooks/customers/data_request",
      callback: async (topic, shop, body, webhookId) => {
        logger.info(`Customer data request received for shop: ${shop}`);
        // Implement GDPR data export logic
      },
    },
    
    CUSTOMERS_REDACT: {
      deliveryMethod: DeliveryMethod.Http,
      callbackUrl: "/webhooks/customers/redact",
      callback: async (topic, shop, body, webhookId) => {
        logger.info(`Customer data redaction request received for shop: ${shop}`);
        // Implement customer data deletion logic
      },
    },
    
    SHOP_REDACT: {
      deliveryMethod: DeliveryMethod.Http,
      callbackUrl: "/webhooks/shop/redact",
      callback: async (topic, shop, body, webhookId) => {
        logger.info(`Shop data redaction request received for shop: ${shop}`);
        // Implement shop data deletion logic
        try {
          await prisma.shop.delete({ where: { shop } });
          await prisma.session.deleteMany({ where: { shop } });
          logger.info(`Deleted all data for shop: ${shop}`);
        } catch (error) {
          logger.error(`Failed to delete shop data for ${shop}:`, error);
        }
      },
    },
    
    // Billing webhooks
    APP_SUBSCRIPTIONS_UPDATE: {
      deliveryMethod: DeliveryMethod.Http,
      callbackUrl: "/webhooks/app_subscriptions/update",
      callback: async (topic, shop, body, webhookId) => {
        logger.info(`App subscription update received for shop: ${shop}`);
        // Handle subscription updates
      },
    },
  },
  
  future: {
    unstable_newEmbeddedAuthStrategy: true,
  },
});

export default shopify;
export const apiVersion = LATEST_API_VERSION;
export const addDocumentResponseHeaders = shopify.addDocumentResponseHeaders;
export const authenticate = shopify.authenticate;
export const unauthenticated = shopify.unauthenticated;
export const login = shopify.login;
export const registerWebhooks = shopify.registerWebhooks;
export const sessionStorage = shopify.sessionStorage;
