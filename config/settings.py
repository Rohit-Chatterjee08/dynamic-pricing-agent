"""
Configuration settings for the Auto-Bundler & Dynamic Pricing Agent system.
"""

import os
from typing import Dict, List, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    VERSION: str = "1.0.0"
    APP_NAME: str = "Auto-Bundler & Dynamic Pricing Agent"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # API Settings
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database Settings
    DATABASE_URL: str = Field(default="sqlite:///./auto_bundler.db", description="Database URL")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Agent Configuration
    COORDINATION_INTERVAL: int = Field(default=300, description="Coordination cycle interval in seconds")
    AUTO_APPLY_BUNDLE_THRESHOLD: float = Field(default=0.8, description="Auto-apply bundle threshold")
    AUTO_APPLY_PRICE_THRESHOLD: float = Field(default=0.85, description="Auto-apply price threshold")
    
    # Inventory Monitor Agent
    INVENTORY_MONITOR_ENABLED: bool = Field(default=True, description="Enable inventory monitor agent")
    INVENTORY_MONITOR_INTERVAL: int = Field(default=300, description="Inventory monitor interval in seconds")
    LOW_STOCK_THRESHOLD: int = Field(default=10, description="Low stock threshold")
    HIGH_STOCK_THRESHOLD: int = Field(default=100, description="High stock threshold")
    SLOW_MOVING_DAYS: int = Field(default=30, description="Days to consider for slow moving items")
    INVENTORY_FORECAST_DAYS: int = Field(default=7, description="Days to forecast inventory")
    
    # Cart Behavior Agent
    CART_BEHAVIOR_ENABLED: bool = Field(default=True, description="Enable cart behavior agent")
    CART_BEHAVIOR_INTERVAL: int = Field(default=600, description="Cart behavior analysis interval in seconds")
    CART_ABANDONMENT_HOURS: int = Field(default=24, description="Cart abandonment threshold in hours")
    MIN_BUNDLE_SUPPORT: float = Field(default=0.1, description="Minimum support for bundle associations")
    MIN_BUNDLE_CONFIDENCE: float = Field(default=0.5, description="Minimum confidence for bundle associations")
    CART_ANALYSIS_LOOKBACK_DAYS: int = Field(default=30, description="Days to look back for cart analysis")
    
    # Competitor Pricing Agent
    COMPETITOR_PRICING_ENABLED: bool = Field(default=True, description="Enable competitor pricing agent")
    COMPETITOR_PRICING_INTERVAL: int = Field(default=900, description="Competitor pricing interval in seconds")
    PRICE_CHANGE_THRESHOLD: float = Field(default=0.05, description="Price change threshold for significance")
    MAX_COMPETITOR_REQUESTS: int = Field(default=5, description="Max concurrent competitor requests")
    COMPETITOR_REQUEST_DELAY: int = Field(default=2, description="Delay between competitor requests")
    COMPETITOR_URLS: Dict[str, List[str]] = Field(default_factory=dict, description="Competitor URLs to monitor")
    
    # Dynamic Bundler Agent
    DYNAMIC_BUNDLER_ENABLED: bool = Field(default=True, description="Enable dynamic bundler agent")
    DYNAMIC_BUNDLER_INTERVAL: int = Field(default=1800, description="Dynamic bundler interval in seconds")
    MIN_BUNDLE_SIZE: int = Field(default=2, description="Minimum bundle size")
    MAX_BUNDLE_SIZE: int = Field(default=4, description="Maximum bundle size")
    MIN_BUNDLE_DISCOUNT: float = Field(default=0.05, description="Minimum bundle discount")
    MAX_BUNDLE_DISCOUNT: float = Field(default=0.25, description="Maximum bundle discount")
    BUNDLE_CONFIDENCE_THRESHOLD: float = Field(default=0.6, description="Bundle confidence threshold")
    
    # Dynamic Pricing Agent
    DYNAMIC_PRICING_ENABLED: bool = Field(default=True, description="Enable dynamic pricing agent")
    DYNAMIC_PRICING_INTERVAL: int = Field(default=600, description="Dynamic pricing interval in seconds")
    MAX_PRICE_INCREASE: float = Field(default=0.20, description="Maximum price increase percentage")
    MAX_PRICE_DECREASE: float = Field(default=0.30, description="Maximum price decrease percentage")
    COMPETITOR_RESPONSE_FACTOR: float = Field(default=0.8, description="Competitor response factor")
    DEMAND_ELASTICITY_THRESHOLD: float = Field(default=-1.5, description="Demand elasticity threshold")
    
    # Machine Learning Settings
    ML_MODELS_ENABLED: bool = Field(default=True, description="Enable ML models")
    MODEL_RETRAIN_INTERVAL: int = Field(default=86400, description="Model retrain interval in seconds")
    DEMAND_FORECAST_HORIZON: int = Field(default=14, description="Demand forecast horizon in days")
    PRICE_ELASTICITY_WINDOW: int = Field(default=90, description="Price elasticity analysis window in days")
    
    # External Service Settings
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis URL for caching")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", description="Celery result backend")
    
    # Monitoring and Alerting
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    PROMETHEUS_PORT: int = Field(default=8001, description="Prometheus metrics port")
    ALERT_EMAIL_ENABLED: bool = Field(default=False, description="Enable email alerts")
    ALERT_EMAIL_RECIPIENTS: List[str] = Field(default_factory=list, description="Alert email recipients")
    SMTP_HOST: str = Field(default="localhost", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    
    # Security Settings
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="Secret key for security")
    API_KEY_REQUIRED: bool = Field(default=False, description="Require API key for endpoints")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Allowed hosts")
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Data Retention
    PRICE_HISTORY_RETENTION_DAYS: int = Field(default=365, description="Price history retention in days")
    RECOMMENDATION_HISTORY_RETENTION_DAYS: int = Field(default=90, description="Recommendation history retention in days")
    CART_DATA_RETENTION_DAYS: int = Field(default=180, description="Cart data retention in days")
    
    # Feature Flags
    ENABLE_AUTO_PRICING: bool = Field(default=True, description="Enable automatic pricing changes")
    ENABLE_AUTO_BUNDLING: bool = Field(default=True, description="Enable automatic bundle creation")
    ENABLE_COMPETITOR_MONITORING: bool = Field(default=True, description="Enable competitor monitoring")
    ENABLE_DEMAND_FORECASTING: bool = Field(default=True, description="Enable demand forecasting")
    
    # Performance Settings
    MAX_CONCURRENT_AGENTS: int = Field(default=10, description="Maximum concurrent agents")
    AGENT_TIMEOUT_SECONDS: int = Field(default=300, description="Agent execution timeout")
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    CACHE_TTL_SECONDS: int = Field(default=300, description="Cache TTL in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.DATABASE_URL.startswith("sqlite"):
            # Ensure SQLite database directory exists
            db_path = self.DATABASE_URL.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        return self.DATABASE_URL
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG
    
    def get_agent_settings(self, agent_name: str) -> Dict[str, Any]:
        """Get settings specific to an agent"""
        agent_settings = {}
        prefix = f"{agent_name.upper()}_"
        
        for key, value in self.__dict__.items():
            if key.startswith(prefix):
                setting_key = key[len(prefix):]
                agent_settings[setting_key] = value
        
        return agent_settings
    
    def validate_settings(self) -> List[str]:
        """Validate settings and return list of issues"""
        issues = []
        
        # Check required settings
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-change-in-production":
            if self.is_production():
                issues.append("SECRET_KEY must be set in production")
        
        # Check threshold values
        if not 0 <= self.AUTO_APPLY_BUNDLE_THRESHOLD <= 1:
            issues.append("AUTO_APPLY_BUNDLE_THRESHOLD must be between 0 and 1")
            
        if not 0 <= self.AUTO_APPLY_PRICE_THRESHOLD <= 1:
            issues.append("AUTO_APPLY_PRICE_THRESHOLD must be between 0 and 1")
        
        # Check agent intervals
        min_interval = 60  # 1 minute minimum
        for interval_setting in [
            "COORDINATION_INTERVAL",
            "INVENTORY_MONITOR_INTERVAL", 
            "CART_BEHAVIOR_INTERVAL",
            "COMPETITOR_PRICING_INTERVAL",
            "DYNAMIC_BUNDLER_INTERVAL",
            "DYNAMIC_PRICING_INTERVAL"
        ]:
            value = getattr(self, interval_setting)
            if value < min_interval:
                issues.append(f"{interval_setting} must be at least {min_interval} seconds")
        
        # Check percentage values
        percentage_settings = [
            ("MIN_BUNDLE_DISCOUNT", self.MIN_BUNDLE_DISCOUNT),
            ("MAX_BUNDLE_DISCOUNT", self.MAX_BUNDLE_DISCOUNT),
            ("MAX_PRICE_INCREASE", self.MAX_PRICE_INCREASE),
            ("MAX_PRICE_DECREASE", self.MAX_PRICE_DECREASE),
        ]
        
        for setting_name, value in percentage_settings:
            if not 0 <= value <= 1:
                issues.append(f"{setting_name} must be between 0 and 1")
        
        # Check bundle discount logic
        if self.MIN_BUNDLE_DISCOUNT >= self.MAX_BUNDLE_DISCOUNT:
            issues.append("MIN_BUNDLE_DISCOUNT must be less than MAX_BUNDLE_DISCOUNT")
        
        # Check bundle size logic
        if self.MIN_BUNDLE_SIZE >= self.MAX_BUNDLE_SIZE:
            issues.append("MIN_BUNDLE_SIZE must be less than MAX_BUNDLE_SIZE")
            
        if self.MIN_BUNDLE_SIZE < 2:
            issues.append("MIN_BUNDLE_SIZE must be at least 2")
        
        return issues


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


def validate_configuration() -> None:
    """Validate the configuration and raise exception if invalid"""
    issues = settings.validate_settings()
    if issues:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {issue}" for issue in issues))


# Configuration presets for different environments
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_ECHO: bool = True
    
    # Faster intervals for development
    COORDINATION_INTERVAL: int = 120
    INVENTORY_MONITOR_INTERVAL: int = 120
    CART_BEHAVIOR_INTERVAL: int = 180
    COMPETITOR_PRICING_INTERVAL: int = 300
    DYNAMIC_BUNDLER_INTERVAL: int = 600
    DYNAMIC_PRICING_INTERVAL: int = 180


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_ECHO: bool = False
    
    # More conservative intervals for production
    COORDINATION_INTERVAL: int = 600
    INVENTORY_MONITOR_INTERVAL: int = 300
    CART_BEHAVIOR_INTERVAL: int = 1200
    COMPETITOR_PRICING_INTERVAL: int = 1800
    DYNAMIC_BUNDLER_INTERVAL: int = 3600
    DYNAMIC_PRICING_INTERVAL: int = 900
    
    # Enhanced security
    API_KEY_REQUIRED: bool = True
    ALLOWED_HOSTS: List[str] = []  # Must be configured
    CORS_ORIGINS: List[str] = []   # Must be configured


class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    DATABASE_URL: str = "sqlite:///:memory:"
    
    # Very fast intervals for testing
    COORDINATION_INTERVAL: int = 10
    INVENTORY_MONITOR_INTERVAL: int = 10
    CART_BEHAVIOR_INTERVAL: int = 10
    COMPETITOR_PRICING_INTERVAL: int = 10
    DYNAMIC_BUNDLER_INTERVAL: int = 10
    DYNAMIC_PRICING_INTERVAL: int = 10
    
    # Disable external services
    REDIS_URL: str = "redis://localhost:6379/15"  # Use test database
    ENABLE_COMPETITOR_MONITORING: bool = False
    PROMETHEUS_ENABLED: bool = False


def get_settings_for_environment(env: str) -> Settings:
    """Get settings for a specific environment"""
    env_lower = env.lower()
    
    if env_lower in ["dev", "development"]:
        return DevelopmentSettings()
    elif env_lower in ["prod", "production"]:
        return ProductionSettings()
    elif env_lower in ["test", "testing"]:
        return TestingSettings()
    else:
        return Settings()


def load_settings_from_file(file_path: str) -> Settings:
    """Load settings from a file"""
    import json
    import yaml
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Settings file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        if file_path.endswith('.json'):
            data = json.load(f)
        elif file_path.endswith(('.yml', '.yaml')):
            data = yaml.safe_load(f)
        else:
            raise ValueError("Settings file must be JSON or YAML")
    
    return Settings(**data)
