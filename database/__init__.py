"""
Database package for the Auto-Bundler & Dynamic Pricing Agent system.
"""

from .connection import DatabaseManager
from .models import Base, Product, PriceHistory, CartData, CompetitorPrice, Bundle, Recommendation, AgentMetric

__all__ = [
    'DatabaseManager',
    'Base',
    'Product',
    'PriceHistory', 
    'CartData',
    'CompetitorPrice',
    'Bundle',
    'Recommendation',
    'AgentMetric'
]
