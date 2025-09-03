"""
Database connection management for the Auto-Bundler & Dynamic Pricing Agent system.
"""

import asyncio
from typing import Any, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import structlog

from .models import Base, Product, PriceHistory, CartData, CompetitorPrice, Bundle, Recommendation, AgentMetric

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Manages database connections and initialization for the agent system"""
    
    def __init__(self, settings: Any):
        self.settings = settings
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        
    async def initialize(self) -> None:
        """Initialize database connections and create tables"""
        try:
            # Convert SQLite URL for async if needed
            database_url = self.settings.get_database_url()
            
            if database_url.startswith("sqlite"):
                # For SQLite, use synchronous engine for table creation
                self.engine = create_engine(
                    database_url,
                    echo=self.settings.DATABASE_ECHO,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
                
                # Create async engine for SQLite
                async_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
                self.async_engine = create_async_engine(
                    async_url,
                    echo=self.settings.DATABASE_ECHO,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
            else:
                # For other databases, use both sync and async engines
                self.engine = create_engine(
                    database_url,
                    echo=self.settings.DATABASE_ECHO,
                    pool_size=self.settings.DATABASE_POOL_SIZE,
                    max_overflow=20
                )
                
                # Convert to async URL
                if database_url.startswith("postgresql"):
                    async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
                elif database_url.startswith("mysql"):
                    async_url = database_url.replace("mysql://", "mysql+aiomysql://")
                else:
                    async_url = database_url
                    
                self.async_engine = create_async_engine(
                    async_url,
                    echo=self.settings.DATABASE_ECHO,
                    pool_size=self.settings.DATABASE_POOL_SIZE,
                    max_overflow=20
                )
            
            # Create session factories
            self.session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False
            )
            
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                expire_on_commit=False
            )
            
            # Create tables
            await self._create_tables()
            
            # Initialize sample data if needed
            await self._initialize_sample_data()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e), exc_info=True)
            raise
    
    async def _create_tables(self) -> None:
        """Create database tables"""
        try:
            if self.engine.dialect.name == "sqlite":
                # For SQLite, use sync engine to create tables
                Base.metadata.create_all(self.engine)
            else:
                # For other databases, use async engine
                async with self.async_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                    
            logger.info("Database tables created")
            
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            raise
    
    async def _initialize_sample_data(self) -> None:
        """Initialize sample data for demonstration"""
        try:
            async with self.get_async_session() as session:
                # Check if we already have products
                from sqlalchemy import select
                result = await session.execute(select(Product))
                existing_products = result.scalars().all()
                
                if not existing_products:
                    # Create sample products
                    sample_products = [
                        Product(
                            id="PROD001",
                            name="Wireless Headphones",
                            category="audio",
                            base_price=99.99,
                            current_price=99.99,
                            cost=50.00,
                            current_stock=5,
                            min_stock=10,
                            max_stock=100,
                            status="active"
                        ),
                        Product(
                            id="PROD002", 
                            name="Smartphone Case",
                            category="mobile_accessories",
                            base_price=19.99,
                            current_price=19.99,
                            cost=8.00,
                            current_stock=150,
                            min_stock=20,
                            max_stock=200,
                            status="active"
                        ),
                        Product(
                            id="PROD003",
                            name="Bluetooth Speaker", 
                            category="audio",
                            base_price=79.99,
                            current_price=79.99,
                            cost=30.00,
                            current_stock=25,
                            min_stock=15,
                            max_stock=80,
                            status="active"
                        ),
                        Product(
                            id="PROD004",
                            name="USB Cable",
                            category="mobile_accessories", 
                            base_price=9.99,
                            current_price=9.99,
                            cost=2.00,
                            current_stock=200,
                            min_stock=50,
                            max_stock=300,
                            status="active"
                        ),
                        Product(
                            id="PROD005",
                            name="Laptop Stand",
                            category="computer_accessories",
                            base_price=39.99,
                            current_price=39.99,
                            cost=15.00,
                            current_stock=8,
                            min_stock=12,
                            max_stock=60,
                            status="active"
                        )
                    ]
                    
                    for product in sample_products:
                        session.add(product)
                    
                    await session.commit()
                    logger.info("Sample products created")
                    
        except Exception as e:
            logger.error("Failed to initialize sample data", error=str(e))
            # Don't raise here as sample data is optional
    
    def get_session(self):
        """Get a synchronous database session"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        return self.session_factory()
    
    def get_async_session(self) -> AsyncSession:
        """Get an asynchronous database session"""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
        return self.async_session_factory()
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.get_async_session() as session:
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    async def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            async with self.get_async_session() as session:
                from sqlalchemy import select, func
                
                stats = {}
                
                # Count records in each table
                tables = [Product, PriceHistory, CartData, CompetitorPrice, Bundle, Recommendation, AgentMetric]
                
                for table in tables:
                    result = await session.execute(select(func.count(table.id)))
                    count = result.scalar()
                    stats[table.__tablename__] = count
                
                return stats
                
        except Exception as e:
            logger.error("Failed to get database stats", error=str(e))
            return {}
    
    async def cleanup_old_data(self) -> None:
        """Clean up old data based on retention settings"""
        try:
            async with self.get_async_session() as session:
                from sqlalchemy import delete
                from datetime import datetime, timedelta
                
                # Clean up old price history
                price_cutoff = datetime.utcnow() - timedelta(days=self.settings.PRICE_HISTORY_RETENTION_DAYS)
                await session.execute(
                    delete(PriceHistory).where(PriceHistory.timestamp < price_cutoff)
                )
                
                # Clean up old recommendations
                rec_cutoff = datetime.utcnow() - timedelta(days=self.settings.RECOMMENDATION_HISTORY_RETENTION_DAYS)
                await session.execute(
                    delete(Recommendation).where(Recommendation.timestamp < rec_cutoff)
                )
                
                # Clean up old cart data
                cart_cutoff = datetime.utcnow() - timedelta(days=self.settings.CART_DATA_RETENTION_DAYS)
                await session.execute(
                    delete(CartData).where(CartData.created_at < cart_cutoff)
                )
                
                await session.commit()
                logger.info("Old data cleanup completed")
                
        except Exception as e:
            logger.error("Failed to cleanup old data", error=str(e))
    
    async def backup_database(self, backup_path: str) -> bool:
        """Create a database backup (SQLite only)"""
        try:
            if not self.settings.get_database_url().startswith("sqlite"):
                logger.warning("Database backup only supported for SQLite")
                return False
            
            import shutil
            db_path = self.settings.get_database_url().replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error("Failed to backup database", error=str(e))
            return False
    
    async def close(self) -> None:
        """Close database connections"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.engine:
                self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Error closing database connections", error=str(e))


# Dependency for FastAPI
async def get_db_session():
    """FastAPI dependency to get database session"""
    # This would be injected by the application
    pass


# Utility functions for common database operations
async def get_product_by_id(session: AsyncSession, product_id: str) -> Optional[Product]:
    """Get product by ID"""
    from sqlalchemy import select
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_active_products(session: AsyncSession) -> list[Product]:
    """Get all active products"""
    from sqlalchemy import select
    result = await session.execute(select(Product).where(Product.status == "active"))
    return result.scalars().all()


async def create_price_history_record(
    session: AsyncSession,
    product_id: str,
    old_price: float,
    new_price: float,
    agent_name: str,
    reason: str
) -> PriceHistory:
    """Create a price history record"""
    record = PriceHistory(
        product_id=product_id,
        old_price=old_price,
        new_price=new_price,
        change_amount=new_price - old_price,
        change_percent=(new_price - old_price) / old_price if old_price > 0 else 0,
        agent_name=agent_name,
        reason=reason
    )
    session.add(record)
    await session.commit()
    return record


async def create_recommendation_record(
    session: AsyncSession,
    agent_name: str,
    recommendation_type: str,
    product_id: Optional[str],
    recommendation: str,
    confidence: float,
    impact: str,
    urgency: str,
    details: dict
) -> Recommendation:
    """Create a recommendation record"""
    record = Recommendation(
        agent_name=agent_name,
        type=recommendation_type,
        product_id=product_id,
        recommendation=recommendation,
        confidence=confidence,
        impact=impact,
        urgency=urgency,
        details=details,
        status="pending"
    )
    session.add(record)
    await session.commit()
    return record


async def update_agent_metrics(
    session: AsyncSession,
    agent_name: str,
    metrics: dict
) -> AgentMetric:
    """Update agent metrics"""
    from sqlalchemy import select
    
    # Try to get existing metrics
    result = await session.execute(
        select(AgentMetric).where(AgentMetric.agent_name == agent_name)
    )
    metric_record = result.scalar_one_or_none()
    
    if metric_record:
        # Update existing record
        metric_record.executions = metrics.get("executions", 0)
        metric_record.successful_executions = metrics.get("successful_executions", 0)
        metric_record.failed_executions = metrics.get("failed_executions", 0)
        metric_record.avg_execution_time = metrics.get("avg_execution_time", 0.0)
        metric_record.total_recommendations = metrics.get("total_recommendations", 0)
        metric_record.accepted_recommendations = metrics.get("accepted_recommendations", 0)
        metric_record.last_execution = metrics.get("last_execution")
        metric_record.updated_at = datetime.utcnow()
    else:
        # Create new record
        metric_record = AgentMetric(
            agent_name=agent_name,
            executions=metrics.get("executions", 0),
            successful_executions=metrics.get("successful_executions", 0),
            failed_executions=metrics.get("failed_executions", 0),
            avg_execution_time=metrics.get("avg_execution_time", 0.0),
            total_recommendations=metrics.get("total_recommendations", 0),
            accepted_recommendations=metrics.get("accepted_recommendations", 0),
            last_execution=metrics.get("last_execution")
        )
        session.add(metric_record)
    
    await session.commit()
    return metric_record
