#!/usr/bin/env node

/**
 * Background worker process for handling Redis queue jobs
 * This runs as a separate process from the main Remix server
 */

import { validateEnv } from '../lib/env.js';
import { webhookQueue, generalQueue } from '../lib/queue.server.js';
import { logger, shopifyLogger, setupGracefulShutdown } from '../lib/logger.server.js';

// Validate environment variables
validateEnv();

let isShuttingDown = false;

async function startWorker() {
  try {
    shopifyLogger.app.started(0); // Worker doesn't have a port
    logger.info('🚀 Background worker started successfully');
    
    // Monitor queue health
    setInterval(async () => {
      try {
        const webhookWaiting = await webhookQueue.waiting();
        const webhookActive = await webhookQueue.active();
        const webhookFailed = await webhookQueue.failed();
        
        const generalWaiting = await generalQueue.waiting();
        const generalActive = await generalQueue.active();
        
        logger.info('Queue health check', {
          webhook: { waiting: webhookWaiting, active: webhookActive, failed: webhookFailed },
          general: { waiting: generalWaiting, active: generalActive }
        });
        
        // Alert on high failure rate
        if (webhookFailed > 10) {
          logger.warn('High webhook failure rate detected', { failed: webhookFailed });
        }
        
      } catch (error) {
        logger.error('Queue health check failed:', error);
      }
    }, 30000); // Every 30 seconds
    
  } catch (error) {
    logger.error('Failed to start worker:', error);
    process.exit(1);
  }
}

// Graceful shutdown handler
async function gracefulShutdown(signal) {
  if (isShuttingDown) {
    logger.info('Force shutdown requested');
    process.exit(1);
  }
  
  isShuttingDown = true;
  shopifyLogger.app.shutdown(signal);
  
  try {
    logger.info('Gracefully shutting down worker...');
    
    // Stop accepting new jobs
    await webhookQueue.pause();
    await generalQueue.pause();
    
    // Wait for active jobs to complete (with timeout)
    const shutdownTimeout = setTimeout(() => {
      logger.warn('Shutdown timeout reached, forcing exit');
      process.exit(1);
    }, 30000); // 30 second timeout
    
    // Wait for all active jobs to complete
    let activeJobs = 0;
    do {
      activeJobs = (await webhookQueue.active()).length + (await generalQueue.active()).length;
      if (activeJobs > 0) {
        logger.info(`Waiting for ${activeJobs} active jobs to complete...`);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    } while (activeJobs > 0);
    
    clearTimeout(shutdownTimeout);
    
    // Close queue connections
    await webhookQueue.close();
    await generalQueue.close();
    
    logger.info('Worker shutdown complete');
    process.exit(0);
    
  } catch (error) {
    logger.error('Error during shutdown:', error);
    process.exit(1);
  }
}

// Setup signal handlers
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
process.on('SIGUSR2', () => gracefulShutdown('SIGUSR2')); // For Nodemon

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception in worker:', error);
  gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection in worker:', { reason, promise });
  gracefulShutdown('unhandledRejection');
});

// Start the worker
startWorker().catch((error) => {
  logger.error('Failed to start worker:', error);
  process.exit(1);
});
