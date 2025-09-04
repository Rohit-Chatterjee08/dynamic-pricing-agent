#!/usr/bin/env node

/**
 * Health check script for production deployment
 * Tests database, Redis, and basic app functionality
 */

const http = require('http');
const { PrismaClient } = require('@prisma/client');
const redis = require('redis');

const HOST = process.env.HOST || 'localhost';
const PORT = process.env.PORT || 3000;
const TIMEOUT = 5000; // 5 second timeout

async function checkDatabase() {
  const prisma = new PrismaClient();
  try {
    await prisma.$queryRaw`SELECT 1`;
    await prisma.$disconnect();
    return { status: 'healthy', message: 'Database connection successful' };
  } catch (error) {
    await prisma.$disconnect();
    return { status: 'unhealthy', message: `Database error: ${error.message}` };
  }
}

async function checkRedis() {
  const client = redis.createClient({
    url: process.env.REDIS_URL,
    socket: {
      connectTimeout: TIMEOUT,
      commandTimeout: TIMEOUT,
    },
  });

  try {
    await client.connect();
    await client.ping();
    await client.quit();
    return { status: 'healthy', message: 'Redis connection successful' };
  } catch (error) {
    try {
      await client.quit();
    } catch (quitError) {
      // Ignore quit errors
    }
    return { status: 'unhealthy', message: `Redis error: ${error.message}` };
  }
}

function checkHttpServer() {
  return new Promise((resolve) => {
    const options = {
      hostname: HOST,
      port: PORT,
      path: '/',
      method: 'GET',
      timeout: TIMEOUT,
    };

    const req = http.request(options, (res) => {
      if (res.statusCode >= 200 && res.statusCode < 400) {
        resolve({ status: 'healthy', message: 'HTTP server responding' });
      } else {
        resolve({ status: 'unhealthy', message: `HTTP server returned ${res.statusCode}` });
      }
    });

    req.on('error', (error) => {
      resolve({ status: 'unhealthy', message: `HTTP server error: ${error.message}` });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({ status: 'unhealthy', message: 'HTTP server timeout' });
    });

    req.setTimeout(TIMEOUT);
    req.end();
  });
}

async function runHealthCheck() {
  console.log('🔍 Running health check...');
  
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    http: await checkHttpServer(),
  };

  const overall = Object.values(checks).every(check => check.status === 'healthy');
  
  const result = {
    status: overall ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    checks,
  };

  console.log(JSON.stringify(result, null, 2));

  // Exit with appropriate code
  process.exit(overall ? 0 : 1);
}

// Handle timeout for entire health check
setTimeout(() => {
  console.error('❌ Health check timeout');
  process.exit(1);
}, TIMEOUT * 2);

runHealthCheck().catch((error) => {
  console.error('❌ Health check failed:', error);
  process.exit(1);
});
