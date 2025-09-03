"""
FastAPI server for the Auto-Bundler & Dynamic Pricing Agent system.
Provides REST API endpoints for monitoring and controlling the agent system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

from config.settings import Settings


# Pydantic models for API requests/responses
class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    base_price: float
    current_price: float
    current_stock: int
    stock_status: str
    status: str


class PriceChangeRequest(BaseModel):
    product_id: str
    new_price: float
    reason: Optional[str] = None


class BundleCreateRequest(BaseModel):
    name: str
    product_ids: List[str]
    discount_percent: Optional[float] = 0.1


class AgentStatusResponse(BaseModel):
    name: str
    status: str
    enabled: bool
    metrics: Dict[str, Any]


class RecommendationResponse(BaseModel):
    id: int
    agent_name: str
    type: str
    product_id: Optional[str]
    recommendation: str
    confidence: float
    impact: str
    urgency: str
    status: str
    timestamp: datetime


class SystemStatusResponse(BaseModel):
    timestamp: datetime
    agents: Dict[str, Any]
    system_metrics: Dict[str, Any]


def create_app(settings: Settings, orchestrator: Any) -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Auto-Bundler & Dynamic Pricing Agent API",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    logger = structlog.get_logger(__name__)
    
    # Dependency to get database session
    async def get_db():
        async with orchestrator.db_manager.get_async_session() as session:
            yield session
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            db_healthy = await orchestrator.db_manager.health_check()
            return {
                "status": "healthy" if db_healthy else "degraded",
                "timestamp": datetime.now().isoformat(),
                "database": "connected" if db_healthy else "disconnected",
                "version": settings.VERSION
            }
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": str(e)}
            )
    
    # System status endpoint
    @app.get("/api/v1/status", response_model=SystemStatusResponse)
    async def get_system_status():
        """Get comprehensive system status"""
        try:
            return await orchestrator.get_system_status()
        except Exception as e:
            logger.error("Failed to get system status", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Agent endpoints
    @app.get("/api/v1/agents", response_model=List[AgentStatusResponse])
    async def get_all_agents():
        """Get status of all agents"""
        try:
            agents_status = []
            for agent_name, agent in orchestrator.agents.items():
                status = await agent.get_status()
                agents_status.append(AgentStatusResponse(**status))
            return agents_status
        except Exception as e:
            logger.error("Failed to get agents status", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/agents/{agent_name}", response_model=AgentStatusResponse)
    async def get_agent_status(agent_name: str):
        """Get status of a specific agent"""
        try:
            if agent_name not in orchestrator.agents:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
            
            agent = orchestrator.agents[agent_name]
            status = await agent.get_status()
            return AgentStatusResponse(**status)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent {agent_name} status", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Product endpoints
    @app.get("/api/v1/products", response_model=List[ProductResponse])
    async def get_products(
        category: Optional[str] = None,
        status: Optional[str] = None,
        stock_status: Optional[str] = None
    ):
        """Get products with optional filtering"""
        try:
            from database.connection import get_active_products
            from sqlalchemy import select
            
            async with orchestrator.db_manager.get_async_session() as session:
                from database.models import Product
                
                query = select(Product)
                
                if category:
                    query = query.where(Product.category == category)
                if status:
                    query = query.where(Product.status == status)
                
                result = await session.execute(query)
                products = result.scalars().all()
                
                response = []
                for product in products:
                    if stock_status and product.stock_status != stock_status:
                        continue
                        
                    response.append(ProductResponse(
                        id=product.id,
                        name=product.name,
                        category=product.category or "",
                        base_price=product.base_price,
                        current_price=product.current_price,
                        current_stock=product.current_stock,
                        stock_status=product.stock_status,
                        status=product.status
                    ))
                
                return response
                
        except Exception as e:
            logger.error("Failed to get products", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
    async def get_product(product_id: str):
        """Get a specific product"""
        try:
            from database.connection import get_product_by_id
            
            async with orchestrator.db_manager.get_async_session() as session:
                product = await get_product_by_id(session, product_id)
                
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
                
                return ProductResponse(
                    id=product.id,
                    name=product.name,
                    category=product.category or "",
                    base_price=product.base_price,
                    current_price=product.current_price,
                    current_stock=product.current_stock,
                    stock_status=product.stock_status,
                    status=product.status
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get product {product_id}", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Price change endpoint
    @app.post("/api/v1/products/{product_id}/price")
    async def change_product_price(product_id: str, price_change: PriceChangeRequest):
        """Manually change product price"""
        try:
            from database.connection import get_product_by_id, create_price_history_record
            
            async with orchestrator.db_manager.get_async_session() as session:
                product = await get_product_by_id(session, product_id)
                
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
                
                old_price = product.current_price
                new_price = price_change.new_price
                
                if new_price <= 0:
                    raise HTTPException(status_code=400, detail="Price must be greater than 0")
                
                # Update product price
                product.current_price = new_price
                
                # Create price history record
                await create_price_history_record(
                    session=session,
                    product_id=product_id,
                    old_price=old_price,
                    new_price=new_price,
                    agent_name="manual",
                    reason=price_change.reason or "Manual price change via API"
                )
                
                return {
                    "product_id": product_id,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_amount": new_price - old_price,
                    "change_percent": (new_price - old_price) / old_price,
                    "timestamp": datetime.now().isoformat()
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to change price for product {product_id}", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Recommendations endpoints
    @app.get("/api/v1/recommendations", response_model=List[RecommendationResponse])
    async def get_recommendations(
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = Query(50, le=500)
    ):
        """Get agent recommendations with optional filtering"""
        try:
            from sqlalchemy import select, desc
            from database.models import Recommendation
            
            async with orchestrator.db_manager.get_async_session() as session:
                query = select(Recommendation).order_by(desc(Recommendation.timestamp))
                
                if agent_name:
                    query = query.where(Recommendation.agent_name == agent_name)
                if status:
                    query = query.where(Recommendation.status == status)
                
                query = query.limit(limit)
                
                result = await session.execute(query)
                recommendations = result.scalars().all()
                
                response = []
                for rec in recommendations:
                    response.append(RecommendationResponse(
                        id=rec.id,
                        agent_name=rec.agent_name,
                        type=rec.type,
                        product_id=rec.product_id,
                        recommendation=rec.recommendation,
                        confidence=rec.confidence,
                        impact=rec.impact,
                        urgency=rec.urgency,
                        status=rec.status,
                        timestamp=rec.timestamp
                    ))
                
                return response
                
        except Exception as e:
            logger.error("Failed to get recommendations", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/api/v1/recommendations/{recommendation_id}/status")
    async def update_recommendation_status(
        recommendation_id: int,
        status: str,
        reviewed_by: Optional[str] = None
    ):
        """Update recommendation status"""
        try:
            from sqlalchemy import select
            from database.models import Recommendation
            
            valid_statuses = ["pending", "accepted", "rejected", "implemented"]
            if status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
            
            async with orchestrator.db_manager.get_async_session() as session:
                result = await session.execute(select(Recommendation).where(Recommendation.id == recommendation_id))
                recommendation = result.scalar_one_or_none()
                
                if not recommendation:
                    raise HTTPException(status_code=404, detail=f"Recommendation {recommendation_id} not found")
                
                recommendation.status = status
                recommendation.reviewed_by = reviewed_by
                recommendation.reviewed_at = datetime.now()
                
                if status == "implemented":
                    recommendation.implemented_at = datetime.now()
                
                await session.commit()
                
                return {
                    "recommendation_id": recommendation_id,
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update recommendation {recommendation_id} status", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Bundle endpoints
    @app.get("/api/v1/bundles")
    async def get_bundles(
        status: Optional[str] = None,
        limit: int = Query(50, le=500)
    ):
        """Get product bundles"""
        try:
            from sqlalchemy import select, desc
            from database.models import Bundle, BundleItem, Product
            
            async with orchestrator.db_manager.get_async_session() as session:
                query = select(Bundle).order_by(desc(Bundle.created_at))
                
                if status:
                    query = query.where(Bundle.status == status)
                
                query = query.limit(limit)
                
                result = await session.execute(query)
                bundles = result.scalars().all()
                
                response = []
                for bundle in bundles:
                    # Get bundle items
                    items_result = await session.execute(
                        select(BundleItem, Product)
                        .join(Product, BundleItem.product_id == Product.id)
                        .where(BundleItem.bundle_id == bundle.bundle_id)
                    )
                    items = items_result.all()
                    
                    bundle_items = []
                    for bundle_item, product in items:
                        bundle_items.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "quantity": bundle_item.quantity,
                            "is_primary": bundle_item.is_primary,
                            "price": bundle_item.price_at_creation
                        })
                    
                    response.append({
                        "bundle_id": bundle.bundle_id,
                        "name": bundle.name,
                        "description": bundle.description,
                        "individual_price": bundle.individual_price,
                        "bundle_price": bundle.bundle_price,
                        "discount_amount": bundle.discount_amount,
                        "discount_percent": bundle.discount_percent,
                        "bundle_type": bundle.bundle_type,
                        "strategy": bundle.strategy,
                        "confidence": bundle.confidence,
                        "views": bundle.views,
                        "conversions": bundle.conversions,
                        "conversion_rate": bundle.conversion_rate,
                        "revenue": bundle.revenue,
                        "status": bundle.status,
                        "created_at": bundle.created_at.isoformat(),
                        "items": bundle_items
                    })
                
                return response
                
        except Exception as e:
            logger.error("Failed to get bundles", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Analytics endpoints
    @app.get("/api/v1/analytics/summary")
    async def get_analytics_summary():
        """Get analytics summary dashboard data"""
        try:
            from sqlalchemy import select, func, desc
            from database.models import Product, PriceHistory, Bundle, Recommendation
            
            async with orchestrator.db_manager.get_async_session() as session:
                # Product metrics
                product_count_result = await session.execute(select(func.count(Product.id)))
                total_products = product_count_result.scalar()
                
                # Active bundles
                active_bundles_result = await session.execute(
                    select(func.count(Bundle.id)).where(Bundle.status == "active")
                )
                active_bundles = active_bundles_result.scalar()
                
                # Recent price changes (last 24 hours)
                yesterday = datetime.now() - timedelta(days=1)
                price_changes_result = await session.execute(
                    select(func.count(PriceHistory.id)).where(PriceHistory.timestamp >= yesterday)
                )
                recent_price_changes = price_changes_result.scalar()
                
                # Pending recommendations
                pending_recs_result = await session.execute(
                    select(func.count(Recommendation.id)).where(Recommendation.status == "pending")
                )
                pending_recommendations = pending_recs_result.scalar()
                
                # Agent performance summary
                agent_summaries = {}
                for agent_name, agent in orchestrator.agents.items():
                    if hasattr(agent, 'get_inventory_summary'):
                        summary = await agent.get_inventory_summary()
                        agent_summaries[agent_name] = summary
                    elif hasattr(agent, 'get_behavior_summary'):
                        summary = await agent.get_behavior_summary()
                        agent_summaries[agent_name] = summary
                    elif hasattr(agent, 'get_competitive_summary'):
                        summary = await agent.get_competitive_summary()
                        agent_summaries[agent_name] = summary
                    elif hasattr(agent, 'get_bundle_summary'):
                        summary = await agent.get_bundle_summary()
                        agent_summaries[agent_name] = summary
                    elif hasattr(agent, 'get_pricing_summary'):
                        summary = await agent.get_pricing_summary()
                        agent_summaries[agent_name] = summary
                
                return {
                    "summary": {
                        "total_products": total_products,
                        "active_bundles": active_bundles,
                        "recent_price_changes": recent_price_changes,
                        "pending_recommendations": pending_recommendations
                    },
                    "agent_summaries": agent_summaries,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error("Failed to get analytics summary", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Configuration endpoint
    @app.get("/api/v1/config")
    async def get_configuration():
        """Get system configuration (non-sensitive data only)"""
        try:
            return {
                "version": settings.VERSION,
                "debug": settings.DEBUG,
                "agents": {
                    "inventory_monitor": settings.INVENTORY_MONITOR_ENABLED,
                    "cart_behavior": settings.CART_BEHAVIOR_ENABLED,
                    "competitor_pricing": settings.COMPETITOR_PRICING_ENABLED,
                    "dynamic_bundler": settings.DYNAMIC_BUNDLER_ENABLED,
                    "dynamic_pricing": settings.DYNAMIC_PRICING_ENABLED
                },
                "intervals": {
                    "coordination": settings.COORDINATION_INTERVAL,
                    "inventory_monitor": settings.INVENTORY_MONITOR_INTERVAL,
                    "cart_behavior": settings.CART_BEHAVIOR_INTERVAL,
                    "competitor_pricing": settings.COMPETITOR_PRICING_INTERVAL,
                    "dynamic_bundler": settings.DYNAMIC_BUNDLER_INTERVAL,
                    "dynamic_pricing": settings.DYNAMIC_PRICING_INTERVAL
                },
                "thresholds": {
                    "low_stock": settings.LOW_STOCK_THRESHOLD,
                    "high_stock": settings.HIGH_STOCK_THRESHOLD,
                    "price_change": settings.PRICE_CHANGE_THRESHOLD,
                    "bundle_confidence": settings.BUNDLE_CONFIDENCE_THRESHOLD
                }
            }
        except Exception as e:
            logger.error("Failed to get configuration", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # Simple web interface
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Simple web dashboard"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Auto-Bundler & Dynamic Pricing Agent Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .card h3 { margin-top: 0; color: #2c3e50; }
                .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
                .metric:last-child { border-bottom: none; }
                .status-healthy { color: #27ae60; }
                .status-warning { color: #f39c12; }
                .status-error { color: #e74c3c; }
                .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
                .btn:hover { background: #2980b9; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Auto-Bundler & Dynamic Pricing Agent</h1>
                    <p>Intelligent pricing and bundling optimization system</p>
                </div>
                
                <div class="cards">
                    <div class="card">
                        <h3>📊 Quick Links</h3>
                        <a href="/docs" class="btn">API Documentation</a>
                        <a href="/api/v1/status" class="btn">System Status</a>
                        <a href="/api/v1/agents" class="btn">Agent Status</a>
                        <a href="/api/v1/analytics/summary" class="btn">Analytics</a>
                    </div>
                    
                    <div class="card">
                        <h3>🎯 Key Features</h3>
                        <div class="metric">
                            <span>Inventory Monitoring</span>
                            <span class="status-healthy">Active</span>
                        </div>
                        <div class="metric">
                            <span>Cart Behavior Analysis</span>
                            <span class="status-healthy">Active</span>
                        </div>
                        <div class="metric">
                            <span>Competitor Price Tracking</span>
                            <span class="status-healthy">Active</span>
                        </div>
                        <div class="metric">
                            <span>Dynamic Bundling</span>
                            <span class="status-healthy">Active</span>
                        </div>
                        <div class="metric">
                            <span>Dynamic Pricing</span>
                            <span class="status-healthy">Active</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>📈 System Overview</h3>
                        <div class="metric">
                            <span>System Status</span>
                            <span class="status-healthy">Running</span>
                        </div>
                        <div class="metric">
                            <span>Active Agents</span>
                            <span>5/5</span>
                        </div>
                        <div class="metric">
                            <span>Last Updated</span>
                            <span id="last-updated">Loading...</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📝 API Examples</h3>
                    <p><strong>Get System Status:</strong> <code>GET /api/v1/status</code></p>
                    <p><strong>Get All Products:</strong> <code>GET /api/v1/products</code></p>
                    <p><strong>Get Recommendations:</strong> <code>GET /api/v1/recommendations</code></p>
                    <p><strong>Get Bundles:</strong> <code>GET /api/v1/bundles</code></p>
                    <p><strong>Change Product Price:</strong> <code>POST /api/v1/products/{id}/price</code></p>
                </div>
            </div>
            
            <script>
                document.getElementById('last-updated').textContent = new Date().toLocaleString();
            </script>
        </body>
        </html>
        """
        return html_content
    
    return app
