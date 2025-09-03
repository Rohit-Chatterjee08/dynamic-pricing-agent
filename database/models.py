"""
Database models for the Auto-Bundler & Dynamic Pricing Agent system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Product(Base):
    """Product model for tracking inventory and pricing"""
    __tablename__ = "products"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Pricing information
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    margin = Column(Float, nullable=True)
    
    # Inventory information
    current_stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer, default=1000)
    reserved_stock = Column(Integer, default=0)
    
    # Product metadata
    sku = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)
    dimensions = Column(String(100), nullable=True)
    
    # Status and tracking
    status = Column(String(20), default="active")  # active, inactive, discontinued
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="product")
    competitor_prices = relationship("CompetitorPrice", back_populates="product")
    bundle_items = relationship("BundleItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id='{self.id}', name='{self.name}', price={self.current_price})>"
    
    @property
    def stock_status(self) -> str:
        """Get stock status based on current levels"""
        if self.current_stock <= 0:
            return "out_of_stock"
        elif self.current_stock <= self.min_stock:
            return "low_stock"
        elif self.current_stock >= self.max_stock:
            return "excess_stock"
        else:
            return "normal"
    
    @property
    def profit_margin(self) -> float:
        """Calculate current profit margin"""
        if self.cost > 0:
            return (self.current_price - self.cost) / self.current_price
        return 0.0


class PriceHistory(Base):
    """Track price changes over time"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    
    # Price change details
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    change_amount = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    
    # Change tracking
    agent_name = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory(product_id='{self.product_id}', change={self.change_percent:.2%})>"


class CartData(Base):
    """Track shopping cart behavior for analysis"""
    __tablename__ = "cart_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Cart metadata
    status = Column(String(20), default="active")  # active, abandoned, completed, expired
    total_value = Column(Float, default=0.0)
    item_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    abandoned_at = Column(DateTime, nullable=True)
    
    # Additional data
    source = Column(String(50), nullable=True)  # web, mobile, api
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Relationships
    items = relationship("CartItem", back_populates="cart")

    def __repr__(self):
        return f"<CartData(cart_id='{self.cart_id}', status='{self.status}', value={self.total_value})>"


class CartItem(Base):
    """Individual items in shopping carts"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(String(100), ForeignKey("cart_data.cart_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, default=1)
    price_at_time = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Timestamps
    added_at = Column(DateTime, default=func.now())
    removed_at = Column(DateTime, nullable=True)
    
    # Relationships
    cart = relationship("CartData", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    def __repr__(self):
        return f"<CartItem(cart_id='{self.cart_id}', product_id='{self.product_id}', qty={self.quantity})>"


class CompetitorPrice(Base):
    """Track competitor pricing data"""
    __tablename__ = "competitor_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    competitor_name = Column(String(100), nullable=False)
    competitor_url = Column(Text, nullable=True)
    
    # Price information
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    shipping_cost = Column(Float, nullable=True)
    availability = Column(String(20), nullable=True)  # in_stock, out_of_stock, limited
    
    # Product matching
    competitor_product_id = Column(String(100), nullable=True)
    competitor_product_name = Column(String(255), nullable=True)
    match_confidence = Column(Float, nullable=True)
    
    # Timestamps
    scraped_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="competitor_prices")

    def __repr__(self):
        return f"<CompetitorPrice(product_id='{self.product_id}', competitor='{self.competitor_name}', price={self.price})>"


class Bundle(Base):
    """Product bundles created by the dynamic bundler"""
    __tablename__ = "bundles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bundle_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing
    individual_price = Column(Float, nullable=False)
    bundle_price = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False)
    
    # Bundle metadata
    bundle_type = Column(String(50), nullable=True)  # association_based, inventory_optimization, etc.
    strategy = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Performance tracking
    views = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Status and timestamps
    status = Column(String(20), default="active")  # active, inactive, expired
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Agent information
    created_by_agent = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("BundleItem", back_populates="bundle")

    def __repr__(self):
        return f"<Bundle(bundle_id='{self.bundle_id}', name='{self.name}', discount={self.discount_percent:.1%})>"
    
    @property
    def conversion_rate(self) -> float:
        """Calculate bundle conversion rate"""
        if self.views > 0:
            return self.conversions / self.views
        return 0.0


class BundleItem(Base):
    """Items within a bundle"""
    __tablename__ = "bundle_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bundle_id = Column(String(100), ForeignKey("bundles.bundle_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    
    # Item details in bundle
    quantity = Column(Integer, default=1)
    is_primary = Column(Boolean, default=False)
    price_at_creation = Column(Float, nullable=False)
    
    # Relationships
    bundle = relationship("Bundle", back_populates="items")
    product = relationship("Product", back_populates="bundle_items")

    def __repr__(self):
        return f"<BundleItem(bundle_id='{self.bundle_id}', product_id='{self.product_id}', qty={self.quantity})>"


class Recommendation(Base):
    """Track agent recommendations and their outcomes"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # price_change, bundle_creation, etc.
    product_id = Column(String(50), nullable=True)
    
    # Recommendation details
    recommendation = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    impact = Column(String(20), nullable=False)  # low, medium, high
    urgency = Column(String(20), nullable=False)  # low, medium, high
    
    # Additional data
    details = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, accepted, rejected, implemented
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    implemented_at = Column(DateTime, nullable=True)
    
    # Outcome tracking
    outcome = Column(String(20), nullable=True)  # successful, failed, partial
    outcome_notes = Column(Text, nullable=True)
    revenue_impact = Column(Float, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Recommendation(agent='{self.agent_name}', type='{self.type}', confidence={self.confidence})>"


class AgentMetric(Base):
    """Track agent performance metrics"""
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False, unique=True)
    
    # Execution metrics
    executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    avg_execution_time = Column(Float, default=0.0)
    last_execution = Column(DateTime, nullable=True)
    
    # Recommendation metrics
    total_recommendations = Column(Integer, default=0)
    accepted_recommendations = Column(Integer, default=0)
    rejected_recommendations = Column(Integer, default=0)
    implemented_recommendations = Column(Integer, default=0)
    
    # Performance metrics
    revenue_generated = Column(Float, default=0.0)
    cost_saved = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AgentMetric(agent='{self.agent_name}', executions={self.executions})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate execution success rate"""
        if self.executions > 0:
            return self.successful_executions / self.executions
        return 0.0
    
    @property
    def recommendation_acceptance_rate(self) -> float:
        """Calculate recommendation acceptance rate"""
        if self.total_recommendations > 0:
            return self.accepted_recommendations / self.total_recommendations
        return 0.0


class SystemEvent(Base):
    """Track system-wide events and alerts"""
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)  # alert, warning, info, error
    source = Column(String(100), nullable=False)  # agent name or system component
    
    # Event details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="info")  # low, medium, high, critical
    
    # Event data
    data = Column(JSON, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="open")  # open, acknowledged, resolved
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<SystemEvent(type='{self.event_type}', source='{self.source}', severity='{self.severity}')>"


class MLModel(Base):
    """Track machine learning models and their performance"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # demand_forecast, price_elasticity, etc.
    version = Column(String(20), nullable=False)
    
    # Model metadata
    algorithm = Column(String(50), nullable=True)
    parameters = Column(JSON, nullable=True)
    features = Column(JSON, nullable=True)
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    
    # Training information
    training_data_size = Column(Integer, nullable=True)
    training_start = Column(DateTime, nullable=True)
    training_end = Column(DateTime, nullable=True)
    training_duration = Column(Float, nullable=True)  # in seconds
    
    # Status and deployment
    status = Column(String(20), default="training")  # training, deployed, retired
    deployed_at = Column(DateTime, nullable=True)
    retired_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MLModel(name='{self.model_name}', type='{self.model_type}', version='{self.version}')>"


# Create indexes for better query performance
from sqlalchemy import Index

# Product indexes
Index('idx_product_category', Product.category)
Index('idx_product_status', Product.status)
Index('idx_product_stock_status', Product.current_stock, Product.min_stock, Product.max_stock)

# Price history indexes
Index('idx_price_history_product_time', PriceHistory.product_id, PriceHistory.timestamp)
Index('idx_price_history_agent', PriceHistory.agent_name)

# Cart data indexes
Index('idx_cart_data_user', CartData.user_id)
Index('idx_cart_data_status_time', CartData.status, CartData.created_at)
Index('idx_cart_items_cart', CartItem.cart_id)

# Competitor price indexes
Index('idx_competitor_price_product_time', CompetitorPrice.product_id, CompetitorPrice.scraped_at)
Index('idx_competitor_price_competitor', CompetitorPrice.competitor_name)

# Bundle indexes
Index('idx_bundle_status_created', Bundle.status, Bundle.created_at)
Index('idx_bundle_performance', Bundle.conversions, Bundle.views)

# Recommendation indexes
Index('idx_recommendation_agent_time', Recommendation.agent_name, Recommendation.timestamp)
Index('idx_recommendation_status', Recommendation.status)

# Agent metric indexes
Index('idx_agent_metrics_name', AgentMetric.agent_name)

# System event indexes
Index('idx_system_events_type_time', SystemEvent.event_type, SystemEvent.timestamp)
Index('idx_system_events_source', SystemEvent.source)
Index('idx_system_events_severity', SystemEvent.severity)
