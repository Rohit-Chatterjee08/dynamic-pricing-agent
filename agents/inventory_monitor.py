"""
Inventory Monitor Agent - Tracks inventory levels, stock movement patterns,
and identifies slow-moving or high-demand products for optimization.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from .base import BaseAgent


class InventoryMonitorAgent(BaseAgent):
    """
    Monitors inventory levels and patterns to identify optimization opportunities.
    
    Key functions:
    - Track inventory levels and movement
    - Identify slow-moving products
    - Detect high-demand items
    - Forecast stock-outs
    - Recommend inventory-based pricing and bundling strategies
    """
    
    def __init__(self, name: str, settings: Any, db_manager: Any, communicator: Any):
        super().__init__(name, settings, db_manager)
        self.communicator = communicator
        
        # Configuration
        self.low_stock_threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 10)
        self.high_stock_threshold = getattr(settings, 'HIGH_STOCK_THRESHOLD', 100)
        self.slow_moving_days = getattr(settings, 'SLOW_MOVING_DAYS', 30)
        self.forecast_days = getattr(settings, 'INVENTORY_FORECAST_DAYS', 7)
        
        # Internal state
        self.inventory_data = {}
        self.movement_history = []
        self.last_analysis = None
    
    async def execute(self) -> None:
        """Main execution logic for inventory monitoring"""
        self.logger.info("Starting inventory monitoring cycle")
        
        try:
            # Fetch current inventory data
            inventory_data = await self._fetch_inventory_data()
            
            # Analyze inventory levels
            inventory_analysis = await self._analyze_inventory_levels(inventory_data)
            
            # Analyze movement patterns
            movement_analysis = await self._analyze_movement_patterns()
            
            # Generate forecasts
            forecasts = await self._generate_inventory_forecasts()
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                inventory_analysis, movement_analysis, forecasts
            )
            
            # Share insights with other agents
            await self._share_inventory_insights({
                "inventory_analysis": inventory_analysis,
                "movement_analysis": movement_analysis,
                "forecasts": forecasts,
                "opportunities": opportunities,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate recommendations
            await self._generate_recommendations(opportunities)
            
            self.last_analysis = datetime.now()
            
        except Exception as e:
            self.logger.error("Inventory monitoring failed", error=str(e), exc_info=True)
            raise
    
    async def _fetch_inventory_data(self) -> Dict[str, Any]:
        """Fetch current inventory data from database"""
        try:
            # In a real implementation, this would query your inventory system
            # For now, we'll simulate with sample data
            
            self.logger.debug("Fetching inventory data")
            
            # Simulate inventory data
            products = [
                {"id": "PROD001", "name": "Wireless Headphones", "current_stock": 5, "cost": 50, "price": 99.99},
                {"id": "PROD002", "name": "Smartphone Case", "current_stock": 150, "cost": 8, "price": 19.99},
                {"id": "PROD003", "name": "Bluetooth Speaker", "current_stock": 25, "cost": 30, "price": 79.99},
                {"id": "PROD004", "name": "USB Cable", "current_stock": 200, "cost": 2, "price": 9.99},
                {"id": "PROD005", "name": "Laptop Stand", "current_stock": 8, "cost": 15, "price": 39.99},
            ]
            
            self.inventory_data = {p["id"]: p for p in products}
            return self.inventory_data
            
        except Exception as e:
            self.logger.error("Failed to fetch inventory data", error=str(e))
            return {}
    
    async def _analyze_inventory_levels(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current inventory levels against thresholds"""
        analysis = {
            "low_stock_items": [],
            "high_stock_items": [],
            "normal_stock_items": [],
            "total_products": len(inventory_data),
            "total_value": 0
        }
        
        for product_id, product in inventory_data.items():
            stock_level = product.get("current_stock", 0)
            value = stock_level * product.get("cost", 0)
            analysis["total_value"] += value
            
            if stock_level <= self.low_stock_threshold:
                analysis["low_stock_items"].append({
                    "product_id": product_id,
                    "name": product.get("name", ""),
                    "current_stock": stock_level,
                    "value": value,
                    "urgency": "high" if stock_level < 5 else "medium"
                })
            elif stock_level >= self.high_stock_threshold:
                analysis["high_stock_items"].append({
                    "product_id": product_id,
                    "name": product.get("name", ""),
                    "current_stock": stock_level,
                    "value": value,
                    "excess_stock": stock_level - self.high_stock_threshold
                })
            else:
                analysis["normal_stock_items"].append({
                    "product_id": product_id,
                    "current_stock": stock_level
                })
        
        self.logger.info(
            "Inventory analysis complete",
            low_stock=len(analysis["low_stock_items"]),
            high_stock=len(analysis["high_stock_items"]),
            total_value=analysis["total_value"]
        )
        
        return analysis
    
    async def _analyze_movement_patterns(self) -> Dict[str, Any]:
        """Analyze historical movement patterns to identify trends"""
        # In a real implementation, this would analyze historical sales data
        # For now, we'll simulate movement analysis
        
        movement_analysis = {
            "fast_moving_items": [
                {"product_id": "PROD002", "velocity": 15.5, "trend": "increasing"},
                {"product_id": "PROD004", "velocity": 12.3, "trend": "stable"}
            ],
            "slow_moving_items": [
                {"product_id": "PROD001", "velocity": 1.2, "trend": "decreasing"},
                {"product_id": "PROD005", "velocity": 2.1, "trend": "stable"}
            ],
            "seasonal_items": [],
            "analysis_period": f"{self.slow_moving_days} days"
        }
        
        self.logger.info(
            "Movement pattern analysis complete",
            fast_moving=len(movement_analysis["fast_moving_items"]),
            slow_moving=len(movement_analysis["slow_moving_items"])
        )
        
        return movement_analysis
    
    async def _generate_inventory_forecasts(self) -> Dict[str, Any]:
        """Generate inventory level forecasts"""
        forecasts = {}
        
        for product_id, product in self.inventory_data.items():
            # Simple forecast based on current velocity
            # In reality, this would use more sophisticated forecasting models
            current_stock = product.get("current_stock", 0)
            
            # Simulate daily sales velocity
            if product_id == "PROD001":
                daily_velocity = 1.2
            elif product_id == "PROD002":
                daily_velocity = 15.5
            elif product_id == "PROD003":
                daily_velocity = 3.8
            elif product_id == "PROD004":
                daily_velocity = 12.3
            else:
                daily_velocity = 2.1
            
            forecasts[product_id] = {
                "current_stock": current_stock,
                "daily_velocity": daily_velocity,
                "forecasted_stockout_date": None,
                "days_until_stockout": None,
                "recommended_reorder": False
            }
            
            if daily_velocity > 0:
                days_until_stockout = current_stock / daily_velocity
                forecasts[product_id]["days_until_stockout"] = days_until_stockout
                
                if days_until_stockout <= self.forecast_days:
                    forecasts[product_id]["forecasted_stockout_date"] = (
                        datetime.now() + timedelta(days=days_until_stockout)
                    ).isoformat()
                    forecasts[product_id]["recommended_reorder"] = True
        
        self.logger.info(
            "Inventory forecasts generated",
            products_forecasted=len(forecasts),
            reorder_recommended=len([f for f in forecasts.values() if f["recommended_reorder"]])
        )
        
        return forecasts
    
    async def _identify_optimization_opportunities(
        self,
        inventory_analysis: Dict[str, Any],
        movement_analysis: Dict[str, Any],
        forecasts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities based on inventory analysis"""
        opportunities = []
        
        # Opportunity 1: Clear high-stock items with discounts
        for item in inventory_analysis["high_stock_items"]:
            opportunities.append({
                "type": "clearance_pricing",
                "product_id": item["product_id"],
                "reason": "High stock levels",
                "recommended_action": "Apply discount to clear excess inventory",
                "confidence": 0.8,
                "potential_impact": "medium",
                "urgency": "low" if item["excess_stock"] < 50 else "medium"
            })
        
        # Opportunity 2: Bundle slow-moving with fast-moving items
        slow_moving_ids = {item["product_id"] for item in movement_analysis["slow_moving_items"]}
        fast_moving_ids = {item["product_id"] for item in movement_analysis["fast_moving_items"]}
        
        for slow_id in slow_moving_ids:
            for fast_id in fast_moving_ids:
                opportunities.append({
                    "type": "bundle_recommendation",
                    "primary_product": fast_id,
                    "bundle_product": slow_id,
                    "reason": "Clear slow-moving inventory with popular items",
                    "recommended_action": "Create bundle offer",
                    "confidence": 0.7,
                    "potential_impact": "high",
                    "urgency": "medium"
                })
        
        # Opportunity 3: Premium pricing for low-stock, high-demand items
        for item in inventory_analysis["low_stock_items"]:
            if item["urgency"] == "high":
                opportunities.append({
                    "type": "premium_pricing",
                    "product_id": item["product_id"],
                    "reason": "Low stock, high demand",
                    "recommended_action": "Increase price to optimize revenue",
                    "confidence": 0.9,
                    "potential_impact": "high",
                    "urgency": "high"
                })
        
        self.logger.info(
            "Optimization opportunities identified",
            total_opportunities=len(opportunities)
        )
        
        return opportunities
    
    async def _share_inventory_insights(self, insights: Dict[str, Any]) -> None:
        """Share inventory insights with other agents"""
        await self.communicator.publish(
            "inventory_update",
            insights,
            self.name
        )
        
        self.logger.debug("Inventory insights shared", insights_keys=list(insights.keys()))
    
    async def _generate_recommendations(self, opportunities: List[Dict[str, Any]]) -> None:
        """Generate and log recommendations based on opportunities"""
        for opportunity in opportunities:
            recommendation = {
                "agent": self.name,
                "type": opportunity["type"],
                "product_id": opportunity.get("product_id"),
                "recommendation": opportunity["recommended_action"],
                "confidence": opportunity["confidence"],
                "impact": opportunity["potential_impact"],
                "urgency": opportunity["urgency"],
                "reason": opportunity["reason"],
                "timestamp": datetime.now().isoformat()
            }
            
            await self.make_recommendation(recommendation)
    
    async def get_inventory_summary(self) -> Dict[str, Any]:
        """Get current inventory summary for API responses"""
        if not self.inventory_data:
            await self._fetch_inventory_data()
        
        total_products = len(self.inventory_data)
        total_stock = sum(p.get("current_stock", 0) for p in self.inventory_data.values())
        total_value = sum(
            p.get("current_stock", 0) * p.get("cost", 0)
            for p in self.inventory_data.values()
        )
        
        low_stock_count = len([
            p for p in self.inventory_data.values()
            if p.get("current_stock", 0) <= self.low_stock_threshold
        ])
        
        high_stock_count = len([
            p for p in self.inventory_data.values()
            if p.get("current_stock", 0) >= self.high_stock_threshold
        ])
        
        return {
            "total_products": total_products,
            "total_stock_units": total_stock,
            "total_inventory_value": total_value,
            "low_stock_items": low_stock_count,
            "high_stock_items": high_stock_count,
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "thresholds": {
                "low_stock": self.low_stock_threshold,
                "high_stock": self.high_stock_threshold
            }
        }
