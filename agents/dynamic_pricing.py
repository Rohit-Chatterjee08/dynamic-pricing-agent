"""
Dynamic Pricing Agent - Adjusts prices in real-time based on demand, competition,
inventory levels, and business objectives to maximize revenue and market position.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import defaultdict

from .base import BaseAgent


class DynamicPricingAgent(BaseAgent):
    """
    Implements intelligent dynamic pricing strategies based on multiple market factors.
    
    Key functions:
    - Monitor demand patterns and price elasticity
    - React to competitor price changes
    - Adjust prices based on inventory levels
    - Implement surge pricing during high demand
    - Optimize prices for revenue and profit maximization
    """
    
    def __init__(self, name: str, settings: Any, db_manager: Any, communicator: Any):
        super().__init__(name, settings, db_manager)
        self.communicator = communicator
        
        # Configuration
        self.max_price_increase = getattr(settings, 'MAX_PRICE_INCREASE', 0.20)  # 20%
        self.max_price_decrease = getattr(settings, 'MAX_PRICE_DECREASE', 0.30)  # 30%
        self.price_change_threshold = getattr(settings, 'PRICE_CHANGE_THRESHOLD', 0.02)  # 2%
        self.competitor_response_factor = getattr(settings, 'COMPETITOR_RESPONSE_FACTOR', 0.8)
        self.demand_elasticity_threshold = getattr(settings, 'DEMAND_ELASTICITY_THRESHOLD', -1.5)
        
        # Internal state
        self.current_prices = {}
        self.price_history = []
        self.demand_patterns = {}
        self.competitor_insights = {}
        self.inventory_insights = {}
        self.pricing_rules = {}
        self.last_analysis = None
        
        # Initialize base prices
        self._initialize_base_prices()
    
    def _initialize_base_prices(self):
        """Initialize base pricing structure"""
        self.current_prices = {
            "PROD001": {"base_price": 99.99, "current_price": 99.99, "min_price": 79.99, "max_price": 119.99},
            "PROD002": {"base_price": 19.99, "current_price": 19.99, "min_price": 14.99, "max_price": 24.99},
            "PROD003": {"base_price": 79.99, "current_price": 79.99, "min_price": 64.99, "max_price": 94.99},
            "PROD004": {"base_price": 9.99, "current_price": 9.99, "min_price": 7.99, "max_price": 12.99},
            "PROD005": {"base_price": 39.99, "current_price": 39.99, "min_price": 29.99, "max_price": 49.99}
        }
    
    async def execute(self) -> None:
        """Main execution logic for dynamic pricing"""
        self.logger.info("Starting dynamic pricing cycle")
        
        try:
            # Gather insights from other agents
            await self._gather_market_insights()
            
            # Analyze demand patterns
            demand_analysis = await self._analyze_demand_patterns()
            
            # Calculate price elasticity
            elasticity_analysis = await self._calculate_price_elasticity()
            
            # Generate pricing strategies
            pricing_strategies = await self._generate_pricing_strategies(
                demand_analysis, elasticity_analysis
            )
            
            # Calculate optimal prices
            optimal_prices = await self._calculate_optimal_prices(pricing_strategies)
            
            # Apply pricing rules and constraints
            validated_prices = await self._validate_and_constrain_prices(optimal_prices)
            
            # Execute price changes
            price_changes = await self._execute_price_changes(validated_prices)
            
            # Monitor pricing performance
            performance_metrics = await self._analyze_pricing_performance()
            
            # Generate pricing recommendations
            await self._generate_pricing_recommendations(
                price_changes, performance_metrics
            )
            
            self.last_analysis = datetime.now()
            
        except Exception as e:
            self.logger.error("Dynamic pricing failed", error=str(e), exc_info=True)
            raise
    
    async def _gather_market_insights(self) -> None:
        """Gather insights from other agents for pricing decisions"""
        # Simulate data from other agents
        self.competitor_insights = {
            "price_changes": [
                {"product_id": "PROD001", "competitor": "competitor_a", "old_price": 89.99, "new_price": 84.99, "change_percent": -0.056},
                {"product_id": "PROD002", "competitor": "competitor_b", "old_price": 18.99, "new_price": 21.99, "change_percent": 0.158}
            ],
            "market_position": {
                "PROD001": {"position": "above_market", "gap": 5.00},
                "PROD002": {"position": "competitive", "gap": 0.50},
                "PROD003": {"position": "competitive", "gap": -2.00},
                "PROD004": {"position": "below_market", "gap": -1.50},
                "PROD005": {"position": "competitive", "gap": 1.00}
            }
        }
        
        self.inventory_insights = {
            "low_stock_items": ["PROD001", "PROD005"],
            "high_stock_items": ["PROD002", "PROD004"],
            "stock_levels": {
                "PROD001": {"current": 5, "target": 20, "status": "critical"},
                "PROD002": {"current": 150, "target": 50, "status": "excess"},
                "PROD003": {"current": 25, "target": 30, "status": "normal"},
                "PROD004": {"current": 200, "target": 75, "status": "excess"},
                "PROD005": {"current": 8, "target": 25, "status": "low"}
            }
        }
        
        # Simulate demand patterns
        self.demand_patterns = {
            "PROD001": {"trend": "declining", "velocity": 1.2, "seasonality": 0.8},
            "PROD002": {"trend": "increasing", "velocity": 15.5, "seasonality": 1.1},
            "PROD003": {"trend": "stable", "velocity": 3.8, "seasonality": 1.0},
            "PROD004": {"trend": "increasing", "velocity": 12.3, "seasonality": 1.2},
            "PROD005": {"trend": "stable", "velocity": 2.1, "seasonality": 0.9}
        }
        
        self.logger.debug("Market insights gathered for pricing analysis")
    
    async def _analyze_demand_patterns(self) -> Dict[str, Any]:
        """Analyze demand patterns to identify pricing opportunities"""
        demand_analysis = {
            "high_demand_products": [],
            "declining_demand_products": [],
            "seasonal_adjustments": {},
            "demand_forecast": {}
        }
        
        for product_id, pattern in self.demand_patterns.items():
            velocity = pattern["velocity"]
            trend = pattern["trend"]
            seasonality = pattern["seasonality"]
            
            # Classify by demand level
            if velocity > 10 and trend == "increasing":
                demand_analysis["high_demand_products"].append({
                    "product_id": product_id,
                    "velocity": velocity,
                    "trend": trend,
                    "pricing_opportunity": "increase"
                })
            elif velocity < 3 and trend in ["declining", "stable"]:
                demand_analysis["declining_demand_products"].append({
                    "product_id": product_id,
                    "velocity": velocity,
                    "trend": trend,
                    "pricing_opportunity": "decrease"
                })
            
            # Seasonal adjustments
            if seasonality != 1.0:
                adjustment_factor = seasonality
                demand_analysis["seasonal_adjustments"][product_id] = {
                    "factor": adjustment_factor,
                    "adjustment": "increase" if adjustment_factor > 1.0 else "decrease",
                    "magnitude": abs(adjustment_factor - 1.0)
                }
            
            # Simple demand forecast (next 7 days)
            current_velocity = velocity * seasonality
            forecasted_demand = current_velocity * 7
            demand_analysis["demand_forecast"][product_id] = {
                "weekly_forecast": forecasted_demand,
                "confidence": 0.7 if trend == "stable" else 0.6
            }
        
        self.logger.info(
            "Demand pattern analysis complete",
            high_demand=len(demand_analysis["high_demand_products"]),
            declining_demand=len(demand_analysis["declining_demand_products"])
        )
        
        return demand_analysis
    
    async def _calculate_price_elasticity(self) -> Dict[str, Any]:
        """Calculate price elasticity of demand for products"""
        # In a real implementation, this would use historical price/demand data
        # For now, we'll simulate elasticity calculations
        
        elasticity_analysis = {}
        
        # Simulate elasticity coefficients based on product characteristics
        product_elasticities = {
            "PROD001": -1.8,  # Elastic (luxury item)
            "PROD002": -0.6,  # Inelastic (necessity)
            "PROD003": -1.2,  # Moderately elastic
            "PROD004": -0.4,  # Inelastic (low price point)
            "PROD005": -1.0   # Unit elastic
        }
        
        for product_id, elasticity in product_elasticities.items():
            current_price = self.current_prices[product_id]["current_price"]
            base_price = self.current_prices[product_id]["base_price"]
            
            # Calculate price sensitivity metrics
            elasticity_analysis[product_id] = {
                "elasticity_coefficient": elasticity,
                "price_sensitivity": "high" if elasticity < -1.5 else "medium" if elasticity < -0.8 else "low",
                "optimal_price_strategy": self._determine_elasticity_strategy(elasticity),
                "revenue_impact_per_1pct_change": self._calculate_revenue_impact(elasticity),
                "current_vs_base_price_ratio": current_price / base_price
            }
        
        return elasticity_analysis
    
    def _determine_elasticity_strategy(self, elasticity: float) -> str:
        """Determine optimal pricing strategy based on elasticity"""
        if elasticity < -2.0:
            return "focus_on_volume"  # Highly elastic - price cuts increase total revenue
        elif elasticity < -1.0:
            return "balanced_approach"  # Moderately elastic - balance price and volume
        else:
            return "focus_on_margin"  # Inelastic - price increases increase total revenue
    
    def _calculate_revenue_impact(self, elasticity: float) -> float:
        """Calculate revenue impact of 1% price change"""
        return 1 + elasticity  # Revenue change = (1 + elasticity) for 1% price increase
    
    async def _generate_pricing_strategies(
        self,
        demand_analysis: Dict[str, Any],
        elasticity_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate pricing strategies based on market analysis"""
        
        strategies = {}
        
        for product_id in self.current_prices.keys():
            strategy_components = []
            
            # Strategy 1: Competitor-based pricing
            competitor_strategy = await self._generate_competitor_strategy(product_id)
            if competitor_strategy:
                strategy_components.append(competitor_strategy)
            
            # Strategy 2: Inventory-based pricing
            inventory_strategy = await self._generate_inventory_strategy(product_id)
            if inventory_strategy:
                strategy_components.append(inventory_strategy)
            
            # Strategy 3: Demand-based pricing
            demand_strategy = await self._generate_demand_strategy(product_id, demand_analysis)
            if demand_strategy:
                strategy_components.append(demand_strategy)
            
            # Strategy 4: Elasticity-based pricing
            elasticity_strategy = await self._generate_elasticity_strategy(product_id, elasticity_analysis)
            if elasticity_strategy:
                strategy_components.append(elasticity_strategy)
            
            strategies[product_id] = {
                "components": strategy_components,
                "primary_strategy": self._select_primary_strategy(strategy_components),
                "confidence": self._calculate_strategy_confidence(strategy_components)
            }
        
        return strategies
    
    async def _generate_competitor_strategy(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Generate competitor-based pricing strategy"""
        market_position = self.competitor_insights.get("market_position", {}).get(product_id)
        price_changes = [pc for pc in self.competitor_insights.get("price_changes", []) if pc["product_id"] == product_id]
        
        if not market_position:
            return None
        
        strategy = {
            "type": "competitor_based",
            "weight": 0.3,
            "recommendation": None,
            "rationale": "",
            "price_adjustment": 0
        }
        
        if market_position["position"] == "above_market":
            gap = market_position["gap"]
            if gap > 5:  # Significant price gap
                adjustment = min(gap * 0.5, self.current_prices[product_id]["current_price"] * 0.1)
                strategy["recommendation"] = "decrease"
                strategy["price_adjustment"] = -adjustment
                strategy["rationale"] = f"Price is ${gap:.2f} above market average"
                strategy["weight"] = 0.4  # Higher weight for significant gaps
        
        elif market_position["position"] == "below_market":
            gap = abs(market_position["gap"])
            if gap > 2:  # Opportunity to increase
                adjustment = min(gap * 0.3, self.current_prices[product_id]["current_price"] * 0.05)
                strategy["recommendation"] = "increase"
                strategy["price_adjustment"] = adjustment
                strategy["rationale"] = f"Price is ${gap:.2f} below market - opportunity for increase"
        
        # React to recent competitor price changes
        for change in price_changes:
            if abs(change["change_percent"]) > 0.05:  # Significant change (>5%)
                reaction_factor = self.competitor_response_factor
                reaction_adjustment = change["change_percent"] * reaction_factor * self.current_prices[product_id]["current_price"]
                
                if strategy["recommendation"] is None:
                    strategy["recommendation"] = "increase" if reaction_adjustment > 0 else "decrease"
                    strategy["price_adjustment"] = reaction_adjustment
                    strategy["rationale"] = f"Reacting to {change['competitor']} price change of {change['change_percent']:.1%}"
                else:
                    # Combine with existing recommendation
                    strategy["price_adjustment"] += reaction_adjustment * 0.5
                    strategy["rationale"] += f"; Also reacting to competitor change"
        
        return strategy if strategy["recommendation"] else None
    
    async def _generate_inventory_strategy(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Generate inventory-based pricing strategy"""
        stock_info = self.inventory_insights.get("stock_levels", {}).get(product_id)
        
        if not stock_info:
            return None
        
        strategy = {
            "type": "inventory_based",
            "weight": 0.25,
            "recommendation": None,
            "rationale": "",
            "price_adjustment": 0
        }
        
        current_stock = stock_info["current"]
        target_stock = stock_info["target"]
        status = stock_info["status"]
        
        if status == "critical":
            # Very low stock - increase price to slow demand
            adjustment = self.current_prices[product_id]["current_price"] * 0.15
            strategy["recommendation"] = "increase"
            strategy["price_adjustment"] = adjustment
            strategy["rationale"] = f"Critical stock level ({current_stock} units) - increase price to manage demand"
            strategy["weight"] = 0.4  # High weight for critical situations
        
        elif status == "low":
            # Low stock - moderate price increase
            adjustment = self.current_prices[product_id]["current_price"] * 0.08
            strategy["recommendation"] = "increase"
            strategy["price_adjustment"] = adjustment
            strategy["rationale"] = f"Low stock level ({current_stock} units) - moderate price increase"
        
        elif status == "excess":
            # Excess stock - decrease price to stimulate demand
            excess_ratio = (current_stock - target_stock) / target_stock
            adjustment = min(self.current_prices[product_id]["current_price"] * 0.12, 
                           self.current_prices[product_id]["current_price"] * excess_ratio * 0.2)
            strategy["recommendation"] = "decrease"
            strategy["price_adjustment"] = -adjustment
            strategy["rationale"] = f"Excess stock ({current_stock} vs target {target_stock}) - decrease to clear inventory"
            strategy["weight"] = 0.35  # Higher weight for excess inventory
        
        return strategy if strategy["recommendation"] else None
    
    async def _generate_demand_strategy(self, product_id: str, demand_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate demand-based pricing strategy"""
        demand_pattern = self.demand_patterns.get(product_id)
        
        if not demand_pattern:
            return None
        
        strategy = {
            "type": "demand_based",
            "weight": 0.2,
            "recommendation": None,
            "rationale": "",
            "price_adjustment": 0
        }
        
        trend = demand_pattern["trend"]
        velocity = demand_pattern["velocity"]
        seasonality = demand_pattern.get("seasonality", 1.0)
        
        # High demand strategy
        if velocity > 10 and trend == "increasing":
            adjustment = self.current_prices[product_id]["current_price"] * 0.08
            strategy["recommendation"] = "increase"
            strategy["price_adjustment"] = adjustment
            strategy["rationale"] = f"High demand trend (velocity: {velocity:.1f}, {trend})"
            strategy["weight"] = 0.3
        
        # Low demand strategy
        elif velocity < 3 and trend in ["declining", "stable"]:
            adjustment = self.current_prices[product_id]["current_price"] * 0.1
            strategy["recommendation"] = "decrease"
            strategy["price_adjustment"] = -adjustment
            strategy["rationale"] = f"Low demand trend (velocity: {velocity:.1f}, {trend})"
            strategy["weight"] = 0.25
        
        # Seasonal adjustment
        if abs(seasonality - 1.0) > 0.1:
            seasonal_adjustment = self.current_prices[product_id]["current_price"] * (seasonality - 1.0) * 0.5
            
            if strategy["recommendation"] is None:
                strategy["recommendation"] = "increase" if seasonal_adjustment > 0 else "decrease"
                strategy["price_adjustment"] = seasonal_adjustment
                strategy["rationale"] = f"Seasonal demand adjustment (factor: {seasonality:.2f})"
            else:
                # Combine with existing recommendation
                strategy["price_adjustment"] += seasonal_adjustment
                strategy["rationale"] += f"; Seasonal factor: {seasonality:.2f}"
        
        return strategy if strategy["recommendation"] else None
    
    async def _generate_elasticity_strategy(self, product_id: str, elasticity_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate elasticity-based pricing strategy"""
        elasticity_info = elasticity_analysis.get(product_id)
        
        if not elasticity_info:
            return None
        
        strategy = {
            "type": "elasticity_based",
            "weight": 0.25,
            "recommendation": None,
            "rationale": "",
            "price_adjustment": 0
        }
        
        elasticity = elasticity_info["elasticity_coefficient"]
        price_sensitivity = elasticity_info["price_sensitivity"]
        optimal_strategy = elasticity_info["optimal_price_strategy"]
        revenue_impact = elasticity_info["revenue_impact_per_1pct_change"]
        
        current_price = self.current_prices[product_id]["current_price"]
        base_price = self.current_prices[product_id]["base_price"]
        
        if optimal_strategy == "focus_on_margin" and current_price < base_price * 1.1:
            # Inelastic product - can increase price for higher revenue
            adjustment = current_price * 0.05  # 5% increase
            strategy["recommendation"] = "increase"
            strategy["price_adjustment"] = adjustment
            strategy["rationale"] = f"Inelastic demand (elasticity: {elasticity:.2f}) - focus on margin"
        
        elif optimal_strategy == "focus_on_volume" and current_price > base_price * 0.9:
            # Elastic product - decrease price to increase volume
            adjustment = current_price * 0.08  # 8% decrease
            strategy["recommendation"] = "decrease"
            strategy["price_adjustment"] = -adjustment
            strategy["rationale"] = f"Elastic demand (elasticity: {elasticity:.2f}) - focus on volume"
        
        return strategy if strategy["recommendation"] else None
    
    def _select_primary_strategy(self, strategy_components: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the primary strategy from multiple components"""
        if not strategy_components:
            return None
        
        # Weight strategies and select the one with highest weighted impact
        weighted_strategies = []
        
        for strategy in strategy_components:
            weight = strategy.get("weight", 0.1)
            adjustment = abs(strategy.get("price_adjustment", 0))
            weighted_impact = weight * adjustment
            
            weighted_strategies.append({
                "strategy": strategy,
                "weighted_impact": weighted_impact
            })
        
        # Sort by weighted impact
        weighted_strategies.sort(key=lambda x: x["weighted_impact"], reverse=True)
        
        return weighted_strategies[0]["strategy"] if weighted_strategies else None
    
    def _calculate_strategy_confidence(self, strategy_components: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the overall pricing strategy"""
        if not strategy_components:
            return 0.0
        
        # Base confidence from number of agreeing strategies
        base_confidence = min(len(strategy_components) * 0.2, 0.8)
        
        # Check for conflicting recommendations
        recommendations = [s.get("recommendation") for s in strategy_components if s.get("recommendation")]
        unique_recommendations = set(recommendations)
        
        if len(unique_recommendations) == 1:
            # All strategies agree
            confidence_boost = 0.2
        elif len(unique_recommendations) == 0:
            # No clear recommendations
            return 0.3
        else:
            # Conflicting recommendations
            confidence_penalty = 0.3
            base_confidence -= confidence_penalty
        
        # Weight-based confidence adjustment
        total_weight = sum(s.get("weight", 0.1) for s in strategy_components)
        weight_confidence = min(total_weight, 0.2)
        
        final_confidence = base_confidence + weight_confidence
        return max(0.1, min(1.0, final_confidence))
    
    async def _calculate_optimal_prices(self, pricing_strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal prices based on strategies"""
        optimal_prices = {}
        
        for product_id, strategy_info in pricing_strategies.items():
            current_price = self.current_prices[product_id]["current_price"]
            
            primary_strategy = strategy_info.get("primary_strategy")
            if not primary_strategy:
                optimal_prices[product_id] = {
                    "recommended_price": current_price,
                    "change_amount": 0,
                    "change_percent": 0,
                    "confidence": 0.3,
                    "rationale": "No clear pricing strategy"
                }
                continue
            
            # Calculate weighted adjustment from all strategies
            total_adjustment = 0
            total_weight = 0
            
            for strategy in strategy_info["components"]:
                adjustment = strategy.get("price_adjustment", 0)
                weight = strategy.get("weight", 0.1)
                total_adjustment += adjustment * weight
                total_weight += weight
            
            # Normalize by total weight
            if total_weight > 0:
                final_adjustment = total_adjustment / total_weight
            else:
                final_adjustment = primary_strategy.get("price_adjustment", 0)
            
            new_price = current_price + final_adjustment
            change_percent = final_adjustment / current_price if current_price > 0 else 0
            
            optimal_prices[product_id] = {
                "recommended_price": round(new_price, 2),
                "change_amount": round(final_adjustment, 2),
                "change_percent": round(change_percent, 4),
                "confidence": strategy_info["confidence"],
                "rationale": primary_strategy.get("rationale", "Strategy-based adjustment"),
                "strategies_used": [s["type"] for s in strategy_info["components"]]
            }
        
        return optimal_prices
    
    async def _validate_and_constrain_prices(self, optimal_prices: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and apply constraints to optimal prices"""
        validated_prices = {}
        
        for product_id, price_info in optimal_prices.items():
            current_price = self.current_prices[product_id]["current_price"]
            recommended_price = price_info["recommended_price"]
            min_price = self.current_prices[product_id]["min_price"]
            max_price = self.current_prices[product_id]["max_price"]
            
            # Apply absolute bounds
            constrained_price = max(min_price, min(max_price, recommended_price))
            
            # Apply maximum change constraints
            max_increase = current_price * (1 + self.max_price_increase)
            max_decrease = current_price * (1 - self.max_price_decrease)
            
            final_price = max(max_decrease, min(max_increase, constrained_price))
            
            # Check minimum change threshold
            change_amount = final_price - current_price
            change_percent = abs(change_amount) / current_price if current_price > 0 else 0
            
            if change_percent < self.price_change_threshold:
                # Change too small, keep current price
                final_price = current_price
                change_amount = 0
                change_percent = 0
                rationale = f"Change too small (< {self.price_change_threshold:.1%}) - no adjustment"
            else:
                rationale = price_info["rationale"]
            
            validated_prices[product_id] = {
                "current_price": current_price,
                "recommended_price": round(final_price, 2),
                "change_amount": round(change_amount, 2),
                "change_percent": round(change_percent, 4),
                "confidence": price_info["confidence"],
                "rationale": rationale,
                "strategies_used": price_info.get("strategies_used", []),
                "constraints_applied": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "max_increase_allowed": max_increase,
                    "max_decrease_allowed": max_decrease,
                    "min_change_threshold": self.price_change_threshold
                }
            }
        
        return validated_prices
    
    async def _execute_price_changes(self, validated_prices: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute validated price changes"""
        price_changes = []
        
        for product_id, price_info in validated_prices.items():
            if price_info["change_amount"] != 0:
                # Update current price
                old_price = self.current_prices[product_id]["current_price"]
                new_price = price_info["recommended_price"]
                
                self.current_prices[product_id]["current_price"] = new_price
                
                # Record the change
                change_record = {
                    "product_id": product_id,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_amount": price_info["change_amount"],
                    "change_percent": price_info["change_percent"],
                    "timestamp": datetime.now().isoformat(),
                    "confidence": price_info["confidence"],
                    "rationale": price_info["rationale"],
                    "strategies_used": price_info.get("strategies_used", [])
                }
                
                price_changes.append(change_record)
                
                # Store in price history
                self.price_history.append(change_record)
                
                self.logger.info(
                    f"Price changed for {product_id}",
                    old_price=old_price,
                    new_price=new_price,
                    change_percent=price_info["change_percent"]
                )
        
        # Keep price history manageable
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]
        
        return price_changes
    
    async def _analyze_pricing_performance(self) -> Dict[str, Any]:
        """Analyze the performance of recent pricing decisions"""
        # In a real implementation, this would analyze actual sales and revenue data
        # For now, we'll simulate performance metrics
        
        performance = {
            "total_price_changes": len([h for h in self.price_history if 
                                      datetime.fromisoformat(h["timestamp"]) > datetime.now() - timedelta(days=7)]),
            "avg_price_change_percent": 0,
            "revenue_impact_estimate": 0,
            "successful_changes": 0,
            "failed_changes": 0,
            "product_performance": {}
        }
        
        recent_changes = [h for h in self.price_history if 
                         datetime.fromisoformat(h["timestamp"]) > datetime.now() - timedelta(days=7)]
        
        if recent_changes:
            performance["avg_price_change_percent"] = np.mean([abs(c["change_percent"]) for c in recent_changes])
            
            # Simulate performance for each product
            for change in recent_changes:
                product_id = change["product_id"]
                
                # Simulate success based on confidence and change direction
                confidence = change["confidence"]
                change_percent = change["change_percent"]
                
                # Higher confidence and smaller changes tend to be more successful
                success_probability = confidence * (1 - abs(change_percent))
                is_successful = np.random.random() < success_probability
                
                if is_successful:
                    performance["successful_changes"] += 1
                    estimated_revenue_impact = abs(change_percent) * 1000  # Simulate revenue impact
                else:
                    performance["failed_changes"] += 1
                    estimated_revenue_impact = -abs(change_percent) * 500  # Negative impact
                
                performance["revenue_impact_estimate"] += estimated_revenue_impact
                
                performance["product_performance"][product_id] = {
                    "success": is_successful,
                    "revenue_impact": estimated_revenue_impact,
                    "confidence": confidence
                }
        
        return performance
    
    async def _generate_pricing_recommendations(
        self,
        price_changes: List[Dict[str, Any]],
        performance_metrics: Dict[str, Any]
    ) -> None:
        """Generate pricing recommendations for the system"""
        
        # Recommend executed price changes
        for change in price_changes:
            recommendation = {
                "agent": self.name,
                "type": "price_change_executed",
                "product_id": change["product_id"],
                "recommendation": f"Changed price from ${change['old_price']:.2f} to ${change['new_price']:.2f}",
                "confidence": change["confidence"],
                "impact": "high" if abs(change["change_percent"]) > 0.1 else "medium",
                "urgency": "immediate",
                "details": {
                    "change_amount": change["change_amount"],
                    "change_percent": change["change_percent"],
                    "rationale": change["rationale"],
                    "strategies": change.get("strategies_used", [])
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.make_recommendation(recommendation)
        
        # Recommend pricing optimizations based on performance
        if performance_metrics["failed_changes"] > performance_metrics["successful_changes"]:
            recommendation = {
                "agent": self.name,
                "type": "pricing_strategy_adjustment",
                "recommendation": "Review pricing strategy - recent changes underperforming",
                "confidence": 0.8,
                "impact": "medium",
                "urgency": "medium",
                "details": {
                    "successful_changes": performance_metrics["successful_changes"],
                    "failed_changes": performance_metrics["failed_changes"],
                    "suggestion": "Consider more conservative pricing changes"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.make_recommendation(recommendation)
    
    async def get_pricing_summary(self) -> Dict[str, Any]:
        """Get current pricing summary for API responses"""
        current_time = datetime.now()
        recent_changes = [
            h for h in self.price_history 
            if datetime.fromisoformat(h["timestamp"]) > current_time - timedelta(days=7)
        ]
        
        # Calculate summary statistics
        total_products = len(self.current_prices)
        products_changed_recently = len(set(c["product_id"] for c in recent_changes))
        avg_price_change = np.mean([abs(c["change_percent"]) for c in recent_changes]) if recent_changes else 0
        
        # Price range analysis
        prices = [p["current_price"] for p in self.current_prices.values()]
        price_range = {
            "min": min(prices),
            "max": max(prices),
            "avg": np.mean(prices)
        }
        
        return {
            "total_products": total_products,
            "products_changed_recently": products_changed_recently,
            "recent_price_changes": len(recent_changes),
            "avg_price_change_percent": round(avg_price_change, 4),
            "price_range": {k: round(v, 2) for k, v in price_range.items()},
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "pricing_strategies_active": {
                "competitor_based": True,
                "inventory_based": True,
                "demand_based": True,
                "elasticity_based": True
            },
            "constraints": {
                "max_increase": f"{self.max_price_increase:.0%}",
                "max_decrease": f"{self.max_price_decrease:.0%}",
                "min_change_threshold": f"{self.price_change_threshold:.1%}"
            }
        }
