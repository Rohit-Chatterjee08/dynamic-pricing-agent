#!/usr/bin/env python3
"""
Auto-Bundler & Dynamic Pricing Agent
Main entry point for the agent system that monitors inventory, cart behavior, 
competitor pricing, and automatically creates dynamic bundles or discounts.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.settings import Settings
from agents.orchestrator import AgentOrchestrator
from database.connection import DatabaseManager
from api.server import create_app


async def main():
    """Main application entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        settings = Settings()
        logger.info(f"Starting Auto-Bundler Agent v{settings.VERSION}")
        
        # Initialize database
        db_manager = DatabaseManager(settings)
        await db_manager.initialize()
        logger.info("Database initialized successfully")
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(settings, db_manager)
        await orchestrator.initialize()
        logger.info("Agent orchestrator initialized")
        
        # Start background agent tasks
        await orchestrator.start_background_tasks()
        logger.info("Background agent tasks started")
        
        # Create and start API server
        app = create_app(settings, orchestrator)
        
        import uvicorn
        config = uvicorn.Config(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level=settings.LOG_LEVEL.lower()
        )
        
        server = uvicorn.Server(config)
        logger.info(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}")
        
        # Run the server
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        if 'orchestrator' in locals():
            await orchestrator.shutdown()
        if 'db_manager' in locals():
            await db_manager.close()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
