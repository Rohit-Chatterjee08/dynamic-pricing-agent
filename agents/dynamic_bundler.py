"""
Dynamic Bundler Agent - Generates intelligent product bundles based on 
inventory levels, customer behavior, and pricing data to maximize AOV.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from itertools import combinations
from collections import defaultdict

from .base import BaseAgent


class DynamicBundlerAgent(BaseAgent):
    """
    Creates intelligent product bundles dynamically based on multiple data sources.
    
    Key functions:
    - Generate bundles based on purchase associations
    - Consider inventory levels for bundle composition
    - Optimize bundle pricing for maximum AOV
    - Create seasonal and promotional bundles
    - Monitor bundle performance and adapt
    """
    
    def __init__(self, name: str, settings: Any, db_manager: Any, communicator: Any):
        super().__init__(name, settings, db_manager)
        self.communicator = communicator
        
        # Configuration
        self.min_bundle_size = getattr(settings, 'MIN_BUNDLE_SIZE', 2)
        self.max_bundle_size = getattr(settings, 'MAX_BUNDLE_SIZE', 4)
        self.min_bundle_discount = getattr(settings, 'MIN_BUNDLE_DISCOUNT', 0.05)  # 5%
        self.max_bundle_discount = getattr(settings, 'MAX_BUNDLE_DISCOUNT', 0.25)  # 25%
        self.bundle_confidence_threshold = getattr(settings, 'BUNDLE_CONFIDENCE_THRESHOLD', 0.6)
        
        # Internal state
        self.active_bundles = {}
        self.bundle_performance = {}
        self.inventory_insights = {}
        self.behavior_insights = {}
        self.pricing_insights = {}
        self.last_analysis = None
    
    async def execute(self) -> None:
        """Main execution logic for dynamic bundling"""
        self.logger.info("Starting dynamic bundling cycle")
        
        try:
            # Wait for insights from other agents
            await self._gather_agent_insights()
            
            # Generate bundle candidates
            bundle_candidates = await self._generate_bundle_candidates()
            
            # Score and rank bundles
            scored_bundles = await self._score_bundles(bundle_candidates)
            
            # Optimize bundle pricing
            optimized_bundles = await self._optimize_bundle_pricing(scored_bundles)
            
            # Select final bundles
            final_bundles = await self._select_final_bundles(optimized_bundles)
            
            # Monitor existing bundle performance
            performance_analysis = await self._analyze_bundle_performance()
            
            # Generate bundle recommendations
            await self._generate_bundle_recommendations(final_bundles, performance_analysis)
            
            # Update active bundles
            await self._update_active_bundles(final_bundles)
            
            self.last_analysis = datetime.now()
            
        except Exception as e:
            self.logger.error("Dynamic bundling failed", error=str(e), exc_info=True)
            raise
    
    async def _gather_agent_insights(self) -> None:
        """Gather insights from other agents for bundle generation"""
        # In a real implementation, this would collect recent messages from other agents
        # For now, we'll simulate the data we'd expect to receive
        
        self.inventory_insights = {
            "low_stock_items": ["PROD001", "PROD005"],
            "high_stock_items": ["PROD002", "PROD004"],
            "slow_moving_items": ["PROD001", "PROD005"],
            "fast_moving_items": ["PROD002", "PROD004"]
        }
        
        self.behavior_insights = {
            "frequently_bought_together": [
                {"items": ["PROD001", "PROD003"], "confidence": 0.75, "lift": 2.1},
                {"items": ["PROD002", "PROD004"], "confidence": 0.85, "lift": 2.8},
                {"items": ["PROD003", "PROD005"], "confidence": 0.65, "lift": 1.9}
            ],
            "high_abandonment_items": ["PROD001"],
            "price_sensitive_ranges": ["100-200"]
        }
        
        self.pricing_insights = {
            "below_market_items": ["PROD004"],
            "above_market_items": ["PROD001"],
            "competitive_items": ["PROD002", "PROD003", "PROD005"]
        }
        
        self.logger.debug("Agent insights gathered for bundling")
    
    async def _generate_bundle_candidates(self) -> List[Dict[str, Any]]:
        """Generate initial bundle candidates based on various strategies"""
        candidates = []
        
        # Strategy 1: Association-based bundles
        association_bundles = await self._create_association_bundles()
        candidates.extend(association_bundles)
        
        # Strategy 2: Inventory optimization bundles
        inventory_bundles = await self._create_inventory_bundles()
        candidates.extend(inventory_bundles)
        
        # Strategy 3: Price-tier bundles
        price_tier_bundles = await self._create_price_tier_bundles()
        candidates.extend(price_tier_bundles)
        
        # Strategy 4: Complementary product bundles
        complementary_bundles = await self._create_complementary_bundles()
        candidates.extend(complementary_bundles)
        
        self.logger.info(f"Generated {len(candidates)} bundle candidates")
        
        return candidates
    
    async def _create_association_bundles(self) -> List[Dict[str, Any]]:
        """Create bundles based on purchase associations"""
        bundles = []
        
        for association in self.behavior_insights.get("frequently_bought_together", []):
            if association["confidence"] >= 0.6 and association["lift"] >= 1.5:
                items = association["items"]
                
                bundles.append({
                    "type": "association_based",
                    "items": items,
                    "base_confidence": association["confidence"],
                    "lift": association["lift"],
                    "strategy": "frequent_together",
                    "primary_item": items[0],  # First item as anchor
                    "reason": f"Items frequently bought together (confidence: {association['confidence']:.2f})"
                })
                
                # Also create reverse bundle with different primary item
                if len(items) >= 2:
                    bundles.append({
                        "type": "association_based",
                        "items": items,
                        "base_confidence": association["confidence"],
                        "lift": association["lift"],
                        "strategy": "frequent_together",
                        "primary_item": items[1],
                        "reason": f"Items frequently bought together (confidence: {association['confidence']:.2f})"
                    })
        
        return bundles
    
    async def _create_inventory_bundles(self) -> List[Dict[str, Any]]:
        """Create bundles to optimize inventory movement"""
        bundles = []
        
        slow_moving = self.inventory_insights.get("slow_moving_items", [])
        fast_moving = self.inventory_insights.get("fast_moving_items", [])
        high_stock = self.inventory_insights.get("high_stock_items", [])
        
        # Pair slow-moving items with fast-moving items
        for slow_item in slow_moving:
            for fast_item in fast_moving:
                if slow_item != fast_item:
                    bundles.append({
                        "type": "inventory_optimization",
                        "items": [fast_item, slow_item],
                        "strategy": "clear_slow_moving",
                        "primary_item": fast_item,
                        "base_confidence": 0.7,
                        "reason": f"Clear slow-moving {slow_item} with popular {fast_item}"
                    })
        
        # Create clearance bundles for high-stock items
        for i, item1 in enumerate(high_stock):
            for item2 in high_stock[i+1:]:
                bundles.append({
                    "type": "inventory_optimization",
                    "items": [item1, item2],
                    "strategy": "clear_excess_stock",
                    "primary_item": item1,
                    "base_confidence": 0.6,
                    "reason": f"Clear excess inventory for {item1} and {item2}"
                })
        
        return bundles
    
    async def _create_price_tier_bundles(self) -> List[Dict[str, Any]]:
        """Create bundles based on price tiers and competitive positioning"""
        bundles = []
        
        # Product prices (simulated)
        product_prices = {
            "PROD001": 99.99,
            "PROD002": 19.99,
            "PROD003": 79.99,
            "PROD004": 9.99,
            "PROD005": 39.99
        }
        
        below_market = self.pricing_insights.get("below_market_items", [])
        above_market = self.pricing_insights.get("above_market_items", [])
        
        # Create value bundles with below-market items as anchors
        for anchor_item in below_market:
            for other_item in product_prices:
                if other_item != anchor_item:
                    bundles.append({
                        "type": "price_optimization",
                        "items": [anchor_item, other_item],
                        "strategy": "value_bundle",
                        "primary_item": anchor_item,
                        "base_confidence": 0.75,
                        "reason": f"Value bundle anchored by competitively priced {anchor_item}"
                    })
        
        # Create premium bundles to justify above-market pricing
        for premium_item in above_market:
            complementary_items = [item for item in product_prices if item != premium_item][:2]
            if complementary_items:
                bundles.append({
                    "type": "price_optimization",
                    "items": [premium_item] + complementary_items,
                    "strategy": "premium_bundle",
                    "primary_item": premium_item,
                    "base_confidence": 0.6,
                    "reason": f"Premium bundle to justify higher price for {premium_item}"
                })
        
        return bundles
    
    async def _create_complementary_bundles(self) -> List[Dict[str, Any]]:
        """Create bundles based on product complementarity"""
        bundles = []
        
        # Define product categories and complementarity (simulated)
        product_categories = {
            "PROD001": "audio",
            "PROD002": "mobile_accessories", 
            "PROD003": "audio",
            "PROD004": "mobile_accessories",
            "PROD005": "computer_accessories"
        }
        
        # Create cross-category bundles
        audio_items = [k for k, v in product_categories.items() if v == "audio"]
        mobile_items = [k for k, v in product_categories.items() if v == "mobile_accessories"]
        computer_items = [k for k, v in product_categories.items() if v == "computer_accessories"]
        
        # Audio + Mobile bundles
        for audio_item in audio_items:
            for mobile_item in mobile_items:
                bundles.append({
                    "type": "complementary",
                    "items": [audio_item, mobile_item],
                    "strategy": "cross_category",
                    "primary_item": audio_item,
                    "base_confidence": 0.65,
                    "reason": f"Complementary audio and mobile accessories"
                })
        
        # Mobile + Computer bundles
        for mobile_item in mobile_items:
            for computer_item in computer_items:
                bundles.append({
                    "type": "complementary",
                    "items": [mobile_item, computer_item],
                    "strategy": "cross_category", 
                    "primary_item": mobile_item,
                    "base_confidence": 0.6,
                    "reason": f"Complementary mobile and computer accessories"
                })
        
        return bundles
    
    async def _score_bundles(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score bundle candidates based on multiple factors"""
        
        for bundle in candidates:
            score_components = {}
            
            # Base confidence from strategy
            score_components["base_confidence"] = bundle.get("base_confidence", 0.5)
            
            # Inventory impact score
            score_components["inventory_impact"] = await self._calculate_inventory_impact(bundle)
            
            # Revenue potential score
            score_components["revenue_potential"] = await self._calculate_revenue_potential(bundle)
            
            # Competitive advantage score
            score_components["competitive_advantage"] = await self._calculate_competitive_advantage(bundle)
            
            # Bundle composition score (diversity, size, etc.)
            score_components["composition_score"] = await self._calculate_composition_score(bundle)
            
            # Calculate weighted final score
            weights = {
                "base_confidence": 0.25,
                "inventory_impact": 0.20,
                "revenue_potential": 0.25,
                "competitive_advantage": 0.15,
                "composition_score": 0.15
            }
            
            final_score = sum(score_components[key] * weights[key] for key in weights)
            
            bundle["score_components"] = score_components
            bundle["final_score"] = final_score
            bundle["confidence"] = min(final_score, 1.0)  # Cap at 1.0
        
        # Sort by final score
        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        
        self.logger.info(f"Scored {len(candidates)} bundle candidates")
        
        return candidates
    
    async def _calculate_inventory_impact(self, bundle: Dict[str, Any]) -> float:
        """Calculate how well the bundle helps with inventory optimization"""
        score = 0.5  # Base score
        
        slow_moving = set(self.inventory_insights.get("slow_moving_items", []))
        high_stock = set(self.inventory_insights.get("high_stock_items", []))
        low_stock = set(self.inventory_insights.get("low_stock_items", []))
        
        bundle_items = set(bundle["items"])
        
        # Bonus for including slow-moving items
        slow_moving_count = len(bundle_items & slow_moving)
        score += slow_moving_count * 0.2
        
        # Bonus for including high-stock items
        high_stock_count = len(bundle_items & high_stock)
        score += high_stock_count * 0.15
        
        # Penalty for including low-stock items (don't want to deplete further)
        low_stock_count = len(bundle_items & low_stock)
        score -= low_stock_count * 0.3
        
        return max(0, min(1, score))
    
    async def _calculate_revenue_potential(self, bundle: Dict[str, Any]) -> float:
        """Calculate the revenue potential of the bundle"""
        # Simulate product prices and margins
        product_data = {
            "PROD001": {"price": 99.99, "margin": 0.5},
            "PROD002": {"price": 19.99, "margin": 0.6},
            "PROD003": {"price": 79.99, "margin": 0.4},
            "PROD004": {"price": 9.99, "margin": 0.7},
            "PROD005": {"price": 39.99, "margin": 0.55}
        }
        
        total_price = sum(product_data.get(item, {}).get("price", 0) for item in bundle["items"])
        total_margin = sum(product_data.get(item, {}).get("margin", 0) for item in bundle["items"])
        avg_margin = total_margin / len(bundle["items"]) if bundle["items"] else 0
        
        # Score based on total value and margin
        price_score = min(total_price / 200, 1.0)  # Normalize to max $200
        margin_score = avg_margin  # Already 0-1
        
        return (price_score * 0.6 + margin_score * 0.4)
    
    async def _calculate_competitive_advantage(self, bundle: Dict[str, Any]) -> float:
        """Calculate competitive advantage of the bundle"""
        score = 0.5
        
        below_market = set(self.pricing_insights.get("below_market_items", []))
        above_market = set(self.pricing_insights.get("above_market_items", []))
        
        bundle_items = set(bundle["items"])
        
        # Bonus for including below-market items (competitive advantage)
        below_market_count = len(bundle_items & below_market)
        score += below_market_count * 0.25
        
        # Slight penalty for above-market items (harder to sell)
        above_market_count = len(bundle_items & above_market)
        score -= above_market_count * 0.1
        
        # Bonus for bundle uniqueness (different strategy)
        if bundle["strategy"] in ["cross_category", "premium_bundle"]:
            score += 0.15
        
        return max(0, min(1, score))
    
    async def _calculate_composition_score(self, bundle: Dict[str, Any]) -> float:
        """Score the bundle composition (size, diversity, etc.)"""
        score = 0.5
        
        # Optimal bundle size (2-3 items typically best)
        bundle_size = len(bundle["items"])
        if 2 <= bundle_size <= 3:
            score += 0.3
        elif bundle_size == 4:
            score += 0.1
        else:
            score -= 0.1
        
        # Bonus for having a clear primary item
        if "primary_item" in bundle:
            score += 0.1
        
        # Bonus for certain strategies
        if bundle["strategy"] in ["frequent_together", "value_bundle"]:
            score += 0.15
        
        return max(0, min(1, score))
    
    async def _optimize_bundle_pricing(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize pricing for each bundle"""
        
        product_prices = {
            "PROD001": 99.99,
            "PROD002": 19.99,
            "PROD003": 79.99,
            "PROD004": 9.99,
            "PROD005": 39.99
        }
        
        for bundle in bundles:
            items = bundle["items"]
            total_individual_price = sum(product_prices.get(item, 0) for item in items)
            
            # Calculate optimal discount based on bundle characteristics
            base_discount = 0.10  # 10% base discount
            
            # Adjust discount based on bundle type
            if bundle["type"] == "inventory_optimization":
                discount = base_discount + 0.08  # Higher discount to clear inventory
            elif bundle["type"] == "association_based":
                discount = base_discount + 0.05  # Moderate discount for proven associations
            elif bundle["type"] == "price_optimization" and bundle["strategy"] == "premium_bundle":
                discount = base_discount + 0.03  # Lower discount for premium bundles
            else:
                discount = base_discount
            
            # Adjust based on confidence
            confidence_multiplier = bundle.get("confidence", 0.5)
            discount *= (0.7 + 0.6 * confidence_multiplier)  # Scale discount by confidence
            
            # Ensure discount is within bounds
            discount = max(self.min_bundle_discount, min(self.max_bundle_discount, discount))
            
            bundle_price = total_individual_price * (1 - discount)
            savings = total_individual_price - bundle_price
            
            bundle["pricing"] = {
                "individual_price": total_individual_price,
                "bundle_price": round(bundle_price, 2),
                "discount_percent": round(discount * 100, 1),
                "savings": round(savings, 2),
                "value_proposition": f"Save ${savings:.2f} ({discount*100:.0f}% off)"
            }
        
        return bundles
    
    async def _select_final_bundles(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select final bundles to activate based on various criteria"""
        
        # Filter by minimum confidence
        qualified_bundles = [
            b for b in bundles 
            if b.get("confidence", 0) >= self.bundle_confidence_threshold
        ]
        
        # Remove duplicate combinations (same items, different primary)
        unique_bundles = []
        seen_combinations = set()
        
        for bundle in qualified_bundles:
            items_key = tuple(sorted(bundle["items"]))
            if items_key not in seen_combinations:
                unique_bundles.append(bundle)
                seen_combinations.add(items_key)
        
        # Limit to top bundles to avoid overwhelming customers
        max_bundles = 10
        selected_bundles = unique_bundles[:max_bundles]
        
        # Ensure diversity in bundle types
        final_bundles = []
        type_counts = defaultdict(int)
        
        for bundle in selected_bundles:
            bundle_type = bundle["type"]
            if type_counts[bundle_type] < 3:  # Max 3 bundles per type
                final_bundles.append(bundle)
                type_counts[bundle_type] += 1
        
        self.logger.info(f"Selected {len(final_bundles)} final bundles from {len(bundles)} candidates")
        
        return final_bundles
    
    async def _analyze_bundle_performance(self) -> Dict[str, Any]:
        """Analyze performance of existing bundles"""
        # In a real implementation, this would analyze actual bundle sales data
        # For now, we'll simulate performance metrics
        
        performance = {
            "active_bundles": len(self.active_bundles),
            "total_bundle_revenue": 0,
            "bundle_conversion_rates": {},
            "top_performing_bundles": [],
            "underperforming_bundles": []
        }
        
        # Simulate performance data for existing bundles
        for bundle_id, bundle in self.active_bundles.items():
            # Simulate metrics
            views = np.random.randint(50, 500)
            conversions = np.random.randint(1, views // 10)
            conversion_rate = conversions / views if views > 0 else 0
            revenue = conversions * bundle.get("pricing", {}).get("bundle_price", 0)
            
            performance["bundle_conversion_rates"][bundle_id] = conversion_rate
            performance["total_bundle_revenue"] += revenue
            
            bundle_perf = {
                "bundle_id": bundle_id,
                "items": bundle["items"],
                "conversion_rate": conversion_rate,
                "revenue": revenue,
                "views": views,
                "conversions": conversions
            }
            
            if conversion_rate > 0.05:  # 5% threshold for good performance
                performance["top_performing_bundles"].append(bundle_perf)
            elif conversion_rate < 0.01:  # 1% threshold for poor performance
                performance["underperforming_bundles"].append(bundle_perf)
        
        return performance
    
    async def _generate_bundle_recommendations(self, bundles: List[Dict[str, Any]], performance: Dict[str, Any]) -> None:
        """Generate bundle recommendations for the system"""
        
        # Recommend new bundles
        for bundle in bundles:
            recommendation = {
                "agent": self.name,
                "type": "bundle_creation",
                "recommendation": f"Create bundle: {', '.join(bundle['items'])}",
                "confidence": bundle["confidence"],
                "impact": "high" if bundle["final_score"] > 0.8 else "medium",
                "urgency": "high" if bundle.get("strategy") == "clear_slow_moving" else "medium",
                "bundle_details": {
                    "items": bundle["items"],
                    "pricing": bundle.get("pricing", {}),
                    "strategy": bundle["strategy"],
                    "reason": bundle["reason"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.make_recommendation(recommendation)
        
        # Recommend discontinuing underperforming bundles
        for bundle_perf in performance.get("underperforming_bundles", []):
            recommendation = {
                "agent": self.name,
                "type": "bundle_discontinuation",
                "recommendation": f"Discontinue underperforming bundle: {', '.join(bundle_perf['items'])}",
                "confidence": 0.8,
                "impact": "medium",
                "urgency": "low",
                "details": {
                    "conversion_rate": bundle_perf["conversion_rate"],
                    "revenue": bundle_perf["revenue"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.make_recommendation(recommendation)
    
    async def _update_active_bundles(self, new_bundles: List[Dict[str, Any]]) -> None:
        """Update the active bundles list"""
        # Add new bundles
        for bundle in new_bundles:
            bundle_id = f"bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(tuple(sorted(bundle['items']))) % 10000}"
            bundle["bundle_id"] = bundle_id
            bundle["created_at"] = datetime.now().isoformat()
            bundle["status"] = "active"
            
            self.active_bundles[bundle_id] = bundle
        
        # Remove old or underperforming bundles (simulate)
        if len(self.active_bundles) > 20:  # Keep max 20 active bundles
            # Remove oldest bundles
            sorted_bundles = sorted(
                self.active_bundles.items(),
                key=lambda x: x[1].get("created_at", "")
            )
            for bundle_id, _ in sorted_bundles[:-20]:
                del self.active_bundles[bundle_id]
        
        self.logger.info(f"Updated active bundles: {len(self.active_bundles)} total")
    
    async def get_bundle_summary(self) -> Dict[str, Any]:
        """Get current bundling summary for API responses"""
        
        # Calculate summary statistics
        active_count = len(self.active_bundles)
        
        bundle_types = defaultdict(int)
        for bundle in self.active_bundles.values():
            bundle_types[bundle.get("type", "unknown")] += 1
        
        avg_bundle_size = np.mean([
            len(bundle.get("items", []))
            for bundle in self.active_bundles.values()
        ]) if self.active_bundles else 0
        
        avg_discount = np.mean([
            bundle.get("pricing", {}).get("discount_percent", 0)
            for bundle in self.active_bundles.values()
        ]) if self.active_bundles else 0
        
        return {
            "active_bundles": active_count,
            "bundle_types": dict(bundle_types),
            "avg_bundle_size": round(avg_bundle_size, 1),
            "avg_discount_percent": round(avg_discount, 1),
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "optimization_strategies": {
                "inventory_based": bundle_types.get("inventory_optimization", 0),
                "behavior_based": bundle_types.get("association_based", 0),
                "price_based": bundle_types.get("price_optimization", 0),
                "complementary": bundle_types.get("complementary", 0)
            }
        }
