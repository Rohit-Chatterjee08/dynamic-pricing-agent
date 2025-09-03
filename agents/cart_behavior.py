"""
Cart Behavior Agent - Analyzes cart abandonment patterns, frequently bought together items,
and user behavior signals to optimize bundling and pricing strategies.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import defaultdict, Counter

from .base import BaseAgent


class CartBehaviorAgent(BaseAgent):
    """
    Analyzes cart and purchase behavior patterns to identify optimization opportunities.
    
    Key functions:
    - Track cart abandonment patterns
    - Identify frequently bought together items
    - Analyze price sensitivity
    - Detect seasonal buying patterns
    - Generate bundle recommendations based on behavior
    """
    
    def __init__(self, name: str, settings: Any, db_manager: Any, communicator: Any):
        super().__init__(name, settings, db_manager)
        self.communicator = communicator
        
        # Configuration
        self.abandonment_threshold_hours = getattr(settings, 'CART_ABANDONMENT_HOURS', 24)
        self.min_support_threshold = getattr(settings, 'MIN_BUNDLE_SUPPORT', 0.1)
        self.min_confidence_threshold = getattr(settings, 'MIN_BUNDLE_CONFIDENCE', 0.5)
        self.lookback_days = getattr(settings, 'CART_ANALYSIS_LOOKBACK_DAYS', 30)
        
        # Internal state
        self.cart_data = []
        self.purchase_data = []
        self.behavior_patterns = {}
        self.last_analysis = None
    
    async def execute(self) -> None:
        """Main execution logic for cart behavior analysis"""
        self.logger.info("Starting cart behavior analysis cycle")
        
        try:
            # Fetch cart and purchase data
            cart_data = await self._fetch_cart_data()
            purchase_data = await self._fetch_purchase_data()
            
            # Analyze abandonment patterns
            abandonment_analysis = await self._analyze_abandonment_patterns(cart_data)
            
            # Analyze item associations
            association_analysis = await self._analyze_item_associations(purchase_data)
            
            # Analyze price sensitivity
            price_sensitivity = await self._analyze_price_sensitivity(cart_data, purchase_data)
            
            # Identify seasonal patterns
            seasonal_patterns = await self._identify_seasonal_patterns(purchase_data)
            
            # Generate behavior insights
            behavior_insights = {
                "abandonment_analysis": abandonment_analysis,
                "association_analysis": association_analysis,
                "price_sensitivity": price_sensitivity,
                "seasonal_patterns": seasonal_patterns,
                "timestamp": datetime.now().isoformat()
            }
            
            # Share insights with other agents
            await self._share_behavior_insights(behavior_insights)
            
            # Generate recommendations
            await self._generate_behavior_recommendations(behavior_insights)
            
            self.last_analysis = datetime.now()
            
        except Exception as e:
            self.logger.error("Cart behavior analysis failed", error=str(e), exc_info=True)
            raise
    
    async def _fetch_cart_data(self) -> List[Dict[str, Any]]:
        """Fetch cart data including abandoned carts"""
        try:
            # In a real implementation, this would query your cart/session data
            # For now, we'll simulate with sample data
            
            self.logger.debug("Fetching cart data")
            
            # Simulate cart data with various scenarios
            base_time = datetime.now() - timedelta(days=30)
            
            cart_data = [
                {
                    "cart_id": "CART001",
                    "user_id": "USER001",
                    "items": [
                        {"product_id": "PROD001", "quantity": 1, "price": 99.99},
                        {"product_id": "PROD003", "quantity": 1, "price": 79.99}
                    ],
                    "created_at": base_time + timedelta(days=1),
                    "last_updated": base_time + timedelta(days=1, hours=2),
                    "status": "abandoned",
                    "total_value": 179.98
                },
                {
                    "cart_id": "CART002",
                    "user_id": "USER002",
                    "items": [
                        {"product_id": "PROD002", "quantity": 2, "price": 19.99},
                        {"product_id": "PROD004", "quantity": 1, "price": 9.99}
                    ],
                    "created_at": base_time + timedelta(days=2),
                    "last_updated": base_time + timedelta(days=2, minutes=30),
                    "status": "completed",
                    "total_value": 49.97
                },
                {
                    "cart_id": "CART003",
                    "user_id": "USER003",
                    "items": [
                        {"product_id": "PROD001", "quantity": 1, "price": 99.99},
                        {"product_id": "PROD005", "quantity": 1, "price": 39.99}
                    ],
                    "created_at": base_time + timedelta(days=3),
                    "last_updated": base_time + timedelta(days=5),
                    "status": "abandoned",
                    "total_value": 139.98
                },
                {
                    "cart_id": "CART004",
                    "user_id": "USER004",
                    "items": [
                        {"product_id": "PROD002", "quantity": 1, "price": 19.99},
                        {"product_id": "PROD004", "quantity": 2, "price": 9.99}
                    ],
                    "created_at": base_time + timedelta(days=5),
                    "last_updated": base_time + timedelta(days=5, minutes=15),
                    "status": "completed",
                    "total_value": 39.97
                }
            ]
            
            self.cart_data = cart_data
            return cart_data
            
        except Exception as e:
            self.logger.error("Failed to fetch cart data", error=str(e))
            return []
    
    async def _fetch_purchase_data(self) -> List[Dict[str, Any]]:
        """Fetch completed purchase data for association analysis"""
        try:
            self.logger.debug("Fetching purchase data")
            
            # Simulate purchase transaction data
            base_time = datetime.now() - timedelta(days=30)
            
            purchase_data = [
                {
                    "transaction_id": "TXN001",
                    "user_id": "USER002",
                    "items": [
                        {"product_id": "PROD002", "quantity": 2, "price": 19.99},
                        {"product_id": "PROD004", "quantity": 1, "price": 9.99}
                    ],
                    "timestamp": base_time + timedelta(days=2),
                    "total_value": 49.97
                },
                {
                    "transaction_id": "TXN002",
                    "user_id": "USER004",
                    "items": [
                        {"product_id": "PROD002", "quantity": 1, "price": 19.99},
                        {"product_id": "PROD004", "quantity": 2, "price": 9.99}
                    ],
                    "timestamp": base_time + timedelta(days=5),
                    "total_value": 39.97
                },
                {
                    "transaction_id": "TXN003",
                    "user_id": "USER005",
                    "items": [
                        {"product_id": "PROD001", "quantity": 1, "price": 99.99},
                        {"product_id": "PROD002", "quantity": 1, "price": 19.99},
                        {"product_id": "PROD004", "quantity": 1, "price": 9.99}
                    ],
                    "timestamp": base_time + timedelta(days=7),
                    "total_value": 129.97
                },
                {
                    "transaction_id": "TXN004",
                    "user_id": "USER006",
                    "items": [
                        {"product_id": "PROD003", "quantity": 1, "price": 79.99},
                        {"product_id": "PROD005", "quantity": 1, "price": 39.99}
                    ],
                    "timestamp": base_time + timedelta(days=10),
                    "total_value": 119.98
                }
            ]
            
            self.purchase_data = purchase_data
            return purchase_data
            
        except Exception as e:
            self.logger.error("Failed to fetch purchase data", error=str(e))
            return []
    
    async def _analyze_abandonment_patterns(self, cart_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cart abandonment patterns to identify triggers and opportunities"""
        abandoned_carts = [cart for cart in cart_data if cart["status"] == "abandoned"]
        completed_carts = [cart for cart in cart_data if cart["status"] == "completed"]
        
        total_carts = len(cart_data)
        abandonment_rate = len(abandoned_carts) / total_carts if total_carts > 0 else 0
        
        # Analyze abandonment by value ranges
        value_ranges = {
            "0-50": [],
            "50-100": [],
            "100-200": [],
            "200+": []
        }
        
        for cart in abandoned_carts:
            value = cart["total_value"]
            if value < 50:
                value_ranges["0-50"].append(cart)
            elif value < 100:
                value_ranges["50-100"].append(cart)
            elif value < 200:
                value_ranges["100-200"].append(cart)
            else:
                value_ranges["200+"].append(cart)
        
        # Analyze most abandoned products
        abandoned_products = Counter()
        for cart in abandoned_carts:
            for item in cart["items"]:
                abandoned_products[item["product_id"]] += item["quantity"]
        
        # Calculate average time in cart before abandonment
        abandonment_times = []
        for cart in abandoned_carts:
            time_diff = cart["last_updated"] - cart["created_at"]
            abandonment_times.append(time_diff.total_seconds() / 3600)  # Convert to hours
        
        avg_abandonment_time = np.mean(abandonment_times) if abandonment_times else 0
        
        analysis = {
            "total_carts": total_carts,
            "abandoned_carts": len(abandoned_carts),
            "completed_carts": len(completed_carts),
            "abandonment_rate": abandonment_rate,
            "avg_abandonment_time_hours": avg_abandonment_time,
            "abandonment_by_value": {
                range_name: len(carts) for range_name, carts in value_ranges.items()
            },
            "most_abandoned_products": dict(abandoned_products.most_common(5)),
            "high_risk_indicators": self._identify_abandonment_risk_factors(abandoned_carts, completed_carts)
        }
        
        self.logger.info(
            "Abandonment analysis complete",
            abandonment_rate=abandonment_rate,
            avg_time=avg_abandonment_time
        )
        
        return analysis
    
    def _identify_abandonment_risk_factors(self, abandoned_carts: List[Dict], completed_carts: List[Dict]) -> List[Dict]:
        """Identify factors that increase abandonment risk"""
        risk_factors = []
        
        # High-value cart risk
        abandoned_values = [cart["total_value"] for cart in abandoned_carts]
        completed_values = [cart["total_value"] for cart in completed_carts]
        
        if abandoned_values and completed_values:
            avg_abandoned_value = np.mean(abandoned_values)
            avg_completed_value = np.mean(completed_values)
            
            if avg_abandoned_value > avg_completed_value * 1.2:
                risk_factors.append({
                    "factor": "high_cart_value",
                    "description": "High-value carts are more likely to be abandoned",
                    "threshold": avg_completed_value * 1.2,
                    "recommendation": "Consider offering incentives for high-value carts"
                })
        
        # Multi-item cart risk
        abandoned_item_counts = [len(cart["items"]) for cart in abandoned_carts]
        completed_item_counts = [len(cart["items"]) for cart in completed_carts]
        
        if abandoned_item_counts and completed_item_counts:
            avg_abandoned_items = np.mean(abandoned_item_counts)
            avg_completed_items = np.mean(completed_item_counts)
            
            if avg_abandoned_items > avg_completed_items:
                risk_factors.append({
                    "factor": "multiple_items",
                    "description": "Carts with multiple items are more likely to be abandoned",
                    "recommendation": "Simplify checkout process or offer bundle discounts"
                })
        
        return risk_factors
    
    async def _analyze_item_associations(self, purchase_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze which items are frequently bought together"""
        # Build transaction matrix
        transactions = []
        for purchase in purchase_data:
            transaction = [item["product_id"] for item in purchase["items"]]
            transactions.append(transaction)
        
        # Calculate item frequencies
        item_counts = Counter()
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        total_transactions = len(transactions)
        
        # Find frequent item pairs (simplified association rule mining)
        item_pairs = Counter()
        association_rules = []
        
        for transaction in transactions:
            # Generate all pairs in this transaction
            items = list(set(transaction))  # Remove duplicates
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    pair = tuple(sorted([items[i], items[j]]))
                    item_pairs[pair] += 1
        
        # Calculate support and confidence for frequent pairs
        for pair, count in item_pairs.items():
            support = count / total_transactions
            
            if support >= self.min_support_threshold:
                item_a, item_b = pair
                
                # Calculate confidence A -> B and B -> A
                confidence_a_to_b = count / item_counts[item_a]
                confidence_b_to_a = count / item_counts[item_b]
                
                if confidence_a_to_b >= self.min_confidence_threshold:
                    association_rules.append({
                        "antecedent": item_a,
                        "consequent": item_b,
                        "support": support,
                        "confidence": confidence_a_to_b,
                        "lift": confidence_a_to_b / (item_counts[item_b] / total_transactions)
                    })
                
                if confidence_b_to_a >= self.min_confidence_threshold:
                    association_rules.append({
                        "antecedent": item_b,
                        "consequent": item_a,
                        "support": support,
                        "confidence": confidence_b_to_a,
                        "lift": confidence_b_to_a / (item_counts[item_a] / total_transactions)
                    })
        
        # Sort by lift (strength of association)
        association_rules.sort(key=lambda x: x["lift"], reverse=True)
        
        analysis = {
            "total_transactions": total_transactions,
            "unique_items": len(item_counts),
            "item_frequencies": dict(item_counts.most_common()),
            "frequent_pairs": dict(item_pairs.most_common(10)),
            "association_rules": association_rules[:20],  # Top 20 rules
            "bundle_recommendations": self._generate_bundle_recommendations(association_rules)
        }
        
        self.logger.info(
            "Association analysis complete",
            total_rules=len(association_rules),
            strong_associations=len([r for r in association_rules if r["lift"] > 1.5])
        )
        
        return analysis
    
    def _generate_bundle_recommendations(self, association_rules: List[Dict]) -> List[Dict]:
        """Generate bundle recommendations from association rules"""
        bundle_recommendations = []
        
        # Group rules by antecedent to find items that go well with others
        antecedent_groups = defaultdict(list)
        for rule in association_rules:
            if rule["lift"] > 1.2:  # Only consider rules with good lift
                antecedent_groups[rule["antecedent"]].append(rule)
        
        for antecedent, rules in antecedent_groups.items():
            if len(rules) >= 1:  # At least one strong association
                # Sort by confidence and pick top associations
                rules.sort(key=lambda x: x["confidence"], reverse=True)
                
                bundle_items = [antecedent]
                total_confidence = 0
                
                for rule in rules[:2]:  # Max 3 items per bundle (1 + 2)
                    bundle_items.append(rule["consequent"])
                    total_confidence += rule["confidence"]
                
                bundle_recommendations.append({
                    "primary_item": antecedent,
                    "bundle_items": bundle_items,
                    "confidence_score": total_confidence / len(rules[:2]),
                    "expected_lift": np.mean([rule["lift"] for rule in rules[:2]]),
                    "bundle_type": "association_based"
                })
        
        # Sort by confidence score
        bundle_recommendations.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        return bundle_recommendations[:10]  # Top 10 bundle recommendations
    
    async def _analyze_price_sensitivity(self, cart_data: List[Dict], purchase_data: List[Dict]) -> Dict[str, Any]:
        """Analyze price sensitivity patterns"""
        # Analyze relationship between cart value and completion rate
        value_brackets = {
            "0-25": {"completed": 0, "abandoned": 0},
            "25-50": {"completed": 0, "abandoned": 0},
            "50-100": {"completed": 0, "abandoned": 0},
            "100-200": {"completed": 0, "abandoned": 0},
            "200+": {"completed": 0, "abandoned": 0}
        }
        
        for cart in cart_data:
            value = cart["total_value"]
            status = cart["status"]
            
            if value < 25:
                bracket = "0-25"
            elif value < 50:
                bracket = "25-50"
            elif value < 100:
                bracket = "50-100"
            elif value < 200:
                bracket = "100-200"
            else:
                bracket = "200+"
            
            if status in ["completed", "abandoned"]:
                value_brackets[bracket][status] += 1
        
        # Calculate completion rates by bracket
        completion_rates = {}
        for bracket, counts in value_brackets.items():
            total = counts["completed"] + counts["abandoned"]
            if total > 0:
                completion_rates[bracket] = counts["completed"] / total
            else:
                completion_rates[bracket] = 0
        
        # Identify optimal price points
        optimal_ranges = []
        for bracket, rate in completion_rates.items():
            if rate > 0.7:  # 70% completion rate threshold
                optimal_ranges.append({
                    "range": bracket,
                    "completion_rate": rate,
                    "recommendation": "Good price range for conversions"
                })
        
        sensitivity_analysis = {
            "completion_by_value_bracket": completion_rates,
            "optimal_price_ranges": optimal_ranges,
            "price_elasticity_indicators": {
                "high_value_abandonment": completion_rates.get("200+", 0) < 0.5,
                "sweet_spot_range": max(completion_rates.items(), key=lambda x: x[1])[0] if completion_rates else None
            }
        }
        
        self.logger.info("Price sensitivity analysis complete")
        
        return sensitivity_analysis
    
    async def _identify_seasonal_patterns(self, purchase_data: List[Dict]) -> Dict[str, Any]:
        """Identify seasonal buying patterns (simplified)"""
        # Group purchases by day of week and hour
        day_patterns = defaultdict(int)
        hour_patterns = defaultdict(int)
        
        for purchase in purchase_data:
            timestamp = purchase["timestamp"]
            day_of_week = timestamp.strftime("%A")
            hour = timestamp.hour
            
            day_patterns[day_of_week] += 1
            hour_patterns[hour] += 1
        
        # Find peak patterns
        peak_day = max(day_patterns.items(), key=lambda x: x[1])[0] if day_patterns else None
        peak_hour = max(hour_patterns.items(), key=lambda x: x[1])[0] if hour_patterns else None
        
        seasonal_analysis = {
            "day_of_week_patterns": dict(day_patterns),
            "hour_of_day_patterns": dict(hour_patterns),
            "peak_shopping_day": peak_day,
            "peak_shopping_hour": peak_hour,
            "recommendations": []
        }
        
        if peak_day:
            seasonal_analysis["recommendations"].append({
                "type": "timing_optimization",
                "recommendation": f"Consider special promotions on {peak_day}s",
                "rationale": "Highest purchase volume day"
            })
        
        self.logger.info("Seasonal pattern analysis complete")
        
        return seasonal_analysis
    
    async def _share_behavior_insights(self, insights: Dict[str, Any]) -> None:
        """Share behavior insights with other agents"""
        await self.communicator.publish(
            "cart_behavior_insight",
            insights,
            self.name
        )
        
        self.logger.debug("Behavior insights shared")
    
    async def _generate_behavior_recommendations(self, insights: Dict[str, Any]) -> None:
        """Generate recommendations based on behavior analysis"""
        recommendations = []
        
        # Abandonment reduction recommendations
        abandonment_data = insights["abandonment_analysis"]
        if abandonment_data["abandonment_rate"] > 0.3:  # 30% threshold
            recommendations.append({
                "type": "abandonment_reduction",
                "recommendation": "Implement cart recovery campaigns",
                "confidence": 0.8,
                "impact": "high",
                "details": f"Current abandonment rate: {abandonment_data['abandonment_rate']:.1%}"
            })
        
        # Bundle recommendations from associations
        for bundle in insights["association_analysis"]["bundle_recommendations"]:
            recommendations.append({
                "type": "bundle_creation",
                "recommendation": f"Create bundle with {', '.join(bundle['bundle_items'])}",
                "confidence": bundle["confidence_score"],
                "impact": "medium",
                "bundle_details": bundle
            })
        
        # Price optimization recommendations
        price_data = insights["price_sensitivity"]
        optimal_ranges = price_data["optimal_price_ranges"]
        if optimal_ranges:
            recommendations.append({
                "type": "price_optimization",
                "recommendation": f"Focus on price ranges: {', '.join([r['range'] for r in optimal_ranges])}",
                "confidence": 0.7,
                "impact": "medium"
            })
        
        # Generate recommendation records
        for rec in recommendations:
            recommendation = {
                "agent": self.name,
                "type": rec["type"],
                "recommendation": rec["recommendation"],
                "confidence": rec["confidence"],
                "impact": rec["impact"],
                "timestamp": datetime.now().isoformat(),
                "details": rec.get("details", "")
            }
            
            await self.make_recommendation(recommendation)
    
    async def get_behavior_summary(self) -> Dict[str, Any]:
        """Get current behavior analysis summary for API responses"""
        if not self.cart_data:
            await self._fetch_cart_data()
            await self._fetch_purchase_data()
        
        total_carts = len(self.cart_data)
        abandoned_carts = len([c for c in self.cart_data if c["status"] == "abandoned"])
        abandonment_rate = abandoned_carts / total_carts if total_carts > 0 else 0
        
        total_transactions = len(self.purchase_data)
        
        return {
            "total_carts_analyzed": total_carts,
            "abandonment_rate": abandonment_rate,
            "total_completed_transactions": total_transactions,
            "analysis_period_days": self.lookback_days,
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "key_insights": {
                "high_abandonment": abandonment_rate > 0.3,
                "sufficient_data": total_carts >= 10
            }
        }
