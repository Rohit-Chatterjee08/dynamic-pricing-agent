#!/usr/bin/env node

/**
 * Production verification script
 * Tests all production components before deployment
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

const CHECK_MARK = '✅';
const CROSS_MARK = '❌';
const WARNING = '⚠️';

let totalChecks = 0;
let passedChecks = 0;
let warnings = 0;

function runCheck(description, fn) {
  totalChecks++;
  process.stdout.write(`${description}... `);
  
  try {
    const result = fn();
    if (result === 'warning') {
      warnings++;
      console.log(`${WARNING} Warning`);
    } else {
      passedChecks++;
      console.log(`${CHECK_MARK} Pass`);
    }
  } catch (error) {
    console.log(`${CROSS_MARK} Fail - ${error.message}`);
  }
}

console.log('🔍 Running Production Verification Checks\n');

// 1. Check required files exist
const requiredFiles = [
  'package.json',
  'Dockerfile',
  'docker-compose.prod.yml',
  '.env.example',
  'tsconfig.json',
  '.eslintrc.json',
  '.prettierrc',
  'DEPLOY.md',
  'PRODUCTION-FIXES.md',
  'shopify.server.ts',
  'prisma/schema.prisma',
  'prisma/migrations/20240904000000_init/migration.sql',
  'lib/env.ts',
  'lib/db.server.ts',
  'lib/crypto.server.ts',
  'lib/security.server.ts',
  'lib/webhooks.server.ts',
  'lib/billing.server.ts',
  'lib/logger.server.ts',
  'lib/queue.server.ts',
  'scripts/start.sh',
  'scripts/healthcheck.js',
  'scripts/worker.js',
  'scripts/init-db.sql',
  '.github/workflows/deploy.yml',
];

requiredFiles.forEach(file => {
  runCheck(`Required file: ${file}`, () => {
    if (!existsSync(file)) {
      throw new Error(`File not found: ${file}`);
    }
    return true;
  });
});

// 2. Check package.json structure
runCheck('Package.json dependencies', () => {
  const pkg = JSON.parse(readFileSync('package.json', 'utf8'));
  
  const requiredDeps = [
    '@shopify/shopify-app-remix',
    '@shopify/app-bridge',
    '@shopify/polaris',
    '@prisma/client',
    'redis',
    'bull',
    'pino',
    'helmet',
    'zod'
  ];
  
  requiredDeps.forEach(dep => {
    if (!pkg.dependencies[dep] && !pkg.devDependencies[dep]) {
      throw new Error(`Missing dependency: ${dep}`);
    }
  });
  
  return true;
});

// 3. Check environment variables
runCheck('Environment variables template', () => {
  const envExample = readFileSync('.env.example', 'utf8');
  
  const requiredVars = [
    'SHOPIFY_API_KEY',
    'SHOPIFY_API_SECRET',
    'SHOPIFY_APP_URL',
    'DATABASE_URL',
    'REDIS_URL',
    'SESSION_SECRET',
    'ENCRYPTION_KEY',
    'SHOPIFY_WEBHOOK_SECRET'
  ];
  
  requiredVars.forEach(varName => {
    if (!envExample.includes(varName)) {
      throw new Error(`Missing env var: ${varName}`);
    }
  });
  
  return true;
});

// 4. Check TypeScript configuration
runCheck('TypeScript configuration', () => {
  const tsConfig = JSON.parse(readFileSync('tsconfig.json', 'utf8'));
  
  if (!tsConfig.compilerOptions.strict) {
    throw new Error('TypeScript strict mode not enabled');
  }
  
  return true;
});

// 5. Check Docker configuration
runCheck('Dockerfile best practices', () => {
  const dockerfile = readFileSync('Dockerfile', 'utf8');
  
  if (!dockerfile.includes('FROM node:18-alpine')) {
    return 'warning'; // Different node version is acceptable
  }
  
  if (!dockerfile.includes('USER nextjs')) {
    throw new Error('Dockerfile should use non-root user');
  }
  
  if (!dockerfile.includes('HEALTHCHECK')) {
    throw new Error('Dockerfile missing health check');
  }
  
  return true;
});

// 6. Check Prisma schema
runCheck('Prisma schema structure', () => {
  const schema = readFileSync('prisma/schema.prisma', 'utf8');
  
  const requiredModels = ['Session', 'Shop', 'Subscription', 'WebhookDelivery'];
  requiredModels.forEach(model => {
    if (!schema.includes(`model ${model}`)) {
      throw new Error(`Missing Prisma model: ${model}`);
    }
  });
  
  if (!schema.includes('extensions = [pgcrypto]')) {
    throw new Error('Missing pgcrypto extension in Prisma schema');
  }
  
  return true;
});

// 7. Check security configuration
runCheck('Security middleware', () => {
  const security = readFileSync('lib/security.server.ts', 'utf8');
  
  if (!security.includes('setupCSP')) {
    throw new Error('Missing CSP configuration');
  }
  
  if (!security.includes('rateLimit')) {
    throw new Error('Missing rate limiting');
  }
  
  if (!security.includes('helmet')) {
    throw new Error('Missing helmet security headers');
  }
  
  return true;
});

// 8. Check webhook processing
runCheck('Webhook processing setup', () => {
  const webhooks = readFileSync('lib/webhooks.server.ts', 'utf8');
  
  if (!webhooks.includes('validateHmac')) {
    throw new Error('Missing HMAC validation');
  }
  
  if (!webhooks.includes('webhookQueue.add')) {
    throw new Error('Missing queue-based processing');
  }
  
  const requiredHandlers = ['app/uninstalled', 'customers/redact', 'shop/redact'];
  requiredHandlers.forEach(handler => {
    if (!webhooks.includes(`'${handler}'`)) {
      throw new Error(`Missing webhook handler: ${handler}`);
    }
  });
  
  return true;
});

// 9. Check logging configuration
runCheck('Logging configuration', () => {
  const logger = readFileSync('lib/logger.server.ts', 'utf8');
  
  if (!logger.includes('pino')) {
    throw new Error('Missing Pino logger');
  }
  
  if (!logger.includes('redact')) {
    throw new Error('Missing sensitive data redaction');
  }
  
  if (!logger.includes('shopifyLogger')) {
    throw new Error('Missing Shopify-specific logging');
  }
  
  return true;
});

// 10. Check GitHub Actions workflow
runCheck('CI/CD pipeline', () => {
  const workflow = readFileSync('.github/workflows/deploy.yml', 'utf8');
  
  if (!workflow.includes('security:')) {
    throw new Error('Missing security audit job');
  }
  
  if (!workflow.includes('test:')) {
    throw new Error('Missing test job');
  }
  
  if (!workflow.includes('postgres:')) {
    throw new Error('Missing PostgreSQL service');
  }
  
  if (!workflow.includes('redis:')) {
    throw new Error('Missing Redis service');
  }
  
  return true;
});

// 11. Check deployment documentation
runCheck('Deployment documentation', () => {
  const deploy = readFileSync('DEPLOY.md', 'utf8');
  
  if (!deploy.includes('Environment Variables')) {
    throw new Error('Missing environment variables section');
  }
  
  if (!deploy.includes('Health Check')) {
    throw new Error('Missing health check documentation');
  }
  
  if (!deploy.includes('Verification')) {
    throw new Error('Missing verification checklist');
  }
  
  return true;
});

// 12. Check if scripts are executable (on Unix systems)
if (process.platform !== 'win32') {
  runCheck('Script permissions', () => {
    try {
      execSync('test -x scripts/start.sh', { stdio: 'ignore' });
    } catch {
      return 'warning'; // Permissions can be fixed during deployment
    }
    return true;
  });
}

// Summary
console.log('\n' + '='.repeat(50));
console.log(`${CHECK_MARK} Passed: ${passedChecks}/${totalChecks}`);
if (warnings > 0) {
  console.log(`${WARNING} Warnings: ${warnings}`);
}

const failed = totalChecks - passedChecks - warnings;
if (failed > 0) {
  console.log(`${CROSS_MARK} Failed: ${failed}`);
  console.log('\n❌ Production verification failed. Please fix the issues above.');
  process.exit(1);
}

if (warnings > 0) {
  console.log('\n⚠️  Production verification passed with warnings. Review warnings before deployment.');
  process.exit(0);
}

console.log('\n🎉 Production verification completed successfully!');
console.log('Your Shopify app is ready for production deployment.');
console.log('\nNext steps:');
console.log('1. Set up your production database (PostgreSQL)');
console.log('2. Set up Redis instance');
console.log('3. Configure environment variables');
console.log('4. Deploy using the instructions in DEPLOY.md');

process.exit(0);
