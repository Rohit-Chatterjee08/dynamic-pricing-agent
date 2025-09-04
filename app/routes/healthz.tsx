import { json } from '@remix-run/node';
import type { LoaderFunctionArgs } from '@remix-run/node';
import { prisma } from '~/lib/db.server';
import { logger, shopifyLogger } from '~/lib/logger.server';
import Redis from 'ioredis';
import { getEnv } from '~/lib/env';

const env = getEnv();

export async function loader({ request }: LoaderFunctionArgs) {
  const startTime = Date.now();
  
  try {
    // Check database connectivity
    const dbStart = Date.now();
    await prisma.$queryRaw`SELECT 1 as health`;
    const dbTime = Date.now() - dbStart;
    
    // Check Redis connectivity
    const redisStart = Date.now();
    const redis = new Redis(env.REDIS_URL, {
      connectTimeout: 3000,
      commandTimeout: 3000,
      maxRetriesPerRequest: 1,
    });
    
    await redis.ping();
    await redis.quit();
    const redisTime = Date.now() - redisStart;
    
    // Get basic app info
    const totalTime = Date.now() - startTime;
    const shopCount = await prisma.shop.count({ where: { isActive: true } });
    const sessionCount = await prisma.session.count();
    
    const healthData = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: env.NODE_ENV,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      checks: {
        database: {
          status: 'healthy',
          responseTime: `${dbTime}ms`,
        },
        redis: {
          status: 'healthy',
          responseTime: `${redisTime}ms`,
        },
        application: {
          status: 'healthy',
          responseTime: `${totalTime}ms`,
        },
      },
      metrics: {
        activeShops: shopCount,
        totalSessions: sessionCount,
        nodeVersion: process.version,
      },
    };
    
    shopifyLogger.app.healthCheck('healthy', healthData);
    
    return json(healthData, {
      status: 200,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Content-Type': 'application/json',
      },
    });
    
  } catch (error) {
    const errorData = {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error',
      checks: {
        database: { status: 'unknown' },
        redis: { status: 'unknown' },
        application: { status: 'unhealthy' },
      },
    };
    
    shopifyLogger.app.healthCheck('unhealthy', errorData);
    logger.error('Health check failed:', error);
    
    return json(errorData, {
      status: 503,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Content-Type': 'application/json',
      },
    });
  }
}

// Simple component for browsers hitting this endpoint
export default function HealthCheck() {
  return (
    <div style={{ 
      fontFamily: 'monospace', 
      padding: '20px', 
      backgroundColor: '#f0f0f0',
      margin: '20px',
      borderRadius: '8px'
    }}>
      <h1>🏥 Health Check</h1>
      <p>This endpoint provides JSON health status when accessed via API.</p>
      <p>For programmatic health checks, send requests with <code>Accept: application/json</code> header.</p>
      <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
        <strong>Checks performed:</strong>
        <ul>
          <li>Database connectivity (PostgreSQL)</li>
          <li>Redis connectivity</li>
          <li>Application health</li>
          <li>Basic metrics collection</li>
        </ul>
      </div>
    </div>
  );
}
