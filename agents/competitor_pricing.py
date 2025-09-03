"""
Competitor Pricing Agent - Monitors competitor prices, tracks market trends,
and identifies pricing opportunities for optimization.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from bs4 import BeautifulSoup
import json
import random

from .base import BaseAgent


class CompetitorPricingAgent(BaseAgent):
    """
    Monitors competitor pricing and market trends to identify optimization opportunities.
    
    Key functions:
    - Track competitor prices across different platforms
    - Analyze pricing trends and patterns
    - Identify pricing gaps and opportunities
    - Monitor price elasticity signals
    - Generate pricing recommendations based on market data
    """
    
    def __init__(self, name: str, settings: Any, db_manager: Any, communicator: Any):
        super().__init__(name, settings, db_manager)
        self.communicator = communicator
        
        # Configuration
        self.competitor_urls = getattr(settings, 'COMPETITOR_URLS', {})
        self.price_change_threshold = getattr(settings, 'PRICE_CHANGE_THRESHOLD', 0.05)  # 5%
        self.max_concurrent_requests = getattr(settings, 'MAX_COMPETITOR_REQUESTS', 5)
        self.request_delay = getattr(settings, 'COMPETITOR_REQUEST_DELAY', 2)  # seconds
        
        # Internal state
        self.current_prices = {}
        self.price_history = []
        self.competitor_data = {}
        self.last_analysis = None
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def execute(self) -> None:
        """Main execution logic for competitor pricing monitoring"""
        self.logger.info("Starting competitor pricing monitoring cycle")
        
        try:
            # Fetch competitor pricing data
            competitor_prices = await self._fetch_competitor_prices()
            
            # Analyze price changes
            price_changes = await self._analyze_price_changes(competitor_prices)
            
            # Identify market trends
            market_trends = await self._analyze_market_trends()
            
            # Find pricing opportunities
            pricing_opportunities = await self._identify_pricing_opportunities(
                competitor_prices, price_changes, market_trends
            )
            
            # Generate competitive analysis
            competitive_analysis = {
                "competitor_prices": competitor_prices,
                "price_changes": price_changes,
                "market_trends": market_trends,
                "pricing_opportunities": pricing_opportunities,
                "timestamp": datetime.now().isoformat()
            }
            
            # Share insights with other agents
            await self._share_pricing_insights(competitive_analysis)
            
            # Generate recommendations
            await self._generate_pricing_recommendations(pricing_opportunities)
            
            self.last_analysis = datetime.now()
            
        except Exception as e:
            self.logger.error("Competitor pricing monitoring failed", error=str(e), exc_info=True)
            raise
    
    async def _fetch_competitor_prices(self) -> Dict[str, Any]:
        """Fetch prices from competitor sources"""
        try:
            self.logger.debug("Fetching competitor prices")
            
            # In a real implementation, this would scrape competitor websites or use APIs
            # For demonstration, we'll simulate competitor data
            
            # Simulate competitor pricing data
            competitors = {
                "competitor_a": {
                    "PROD001": {"price": 89.99, "availability": "in_stock", "shipping": "free"},
                    "PROD002": {"price": 22.99, "availability": "in_stock", "shipping": "3.99"},
                    "PROD003": {"price": 74.99, "availability": "low_stock", "shipping": "free"},
                    "PROD004": {"price": 8.99, "availability": "in_stock", "shipping": "2.99"},
                    "PROD005": {"price": 44.99, "availability": "in_stock", "shipping": "free"}
                },
                "competitor_b": {
                    "PROD001": {"price": 94.99, "availability": "in_stock", "shipping": "free"},
                    "PROD002": {"price": 18.99, "availability": "in_stock", "shipping": "free"},
                    "PROD003": {"price": 82.99, "availability": "in_stock", "shipping": "4.99"},
                    "PROD004": {"price": 11.99, "availability": "in_stock", "shipping": "free"},
                    "PROD005": {"price": 37.99, "availability": "out_of_stock", "shipping": "free"}
                },
                "competitor_c": {
                    "PROD001": {"price": 99.99, "availability": "in_stock", "shipping": "5.99"},
                    "PROD002": {"price": 19.99, "availability": "in_stock", "shipping": "free"},
                    "PROD003": {"price": 79.99, "availability": "in_stock", "shipping": "free"},
                    "PROD004": {"price": 9.99, "availability": "in_stock", "shipping": "3.99"},
                    "PROD005": {"price": 42.99, "availability": "in_stock", "shipping": "free"}
                }
            }
            
            # Add some randomness to simulate price fluctuations
            for competitor, products in competitors.items():
                for product_id, data in products.items():
                    # Add small random variation (±5%)
                    variation = random.uniform(-0.05, 0.05)
                    data["price"] *= (1 + variation)
                    data["price"] = round(data["price"], 2)
            
            self.competitor_data = competitors
            
            # Store historical data
            timestamp = datetime.now()
            for competitor, products in competitors.items():
                for product_id, data in products.items():
                    self.price_history.append({
                        "timestamp": timestamp,
                        "competitor": competitor,
                        "product_id": product_id,
                        "price": data["price"],
                        "availability": data["availability"]
                    })
            
            # Keep only last 100 records per product to prevent memory issues
            self.price_history = self.price_history[-1000:]
            
            self.logger.info(
                "Competitor prices fetched",
                competitors=len(competitors),
                products_monitored=len(set(p["product_id"] for p in self.price_history[-50:]))
            )
            
            return competitors
            
        except Exception as e:
            self.logger.error("Failed to fetch competitor prices", error=str(e))
            return {}
    
    async def _analyze_price_changes(self, current_prices: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze recent price changes across competitors"""
        price_changes = {
            "significant_changes": [],
            "trend_analysis": {},
            "market_position": {}
        }
        
        if len(self.price_history) < 10:  # Need some history for analysis
            return price_changes
        
        # Group price history by product
        product_prices = {}
        for record in self.price_history[-50:]:  # Look at last 50 records
            product_id = record["product_id"]
            if product_id not in product_prices:
                product_prices[product_id] = []
            product_prices[product_id].append(record)
        
        # Analyze each product
        for product_id, records in product_prices.items():
            if len(records) < 3:  # Need at least 3 data points
                continue
            
            # Sort by timestamp
            records.sort(key=lambda x: x["timestamp"])
            
            # Calculate price trends by competitor
            competitor_trends = {}
            for competitor in set(r["competitor"] for r in records):
                competitor_records = [r for r in records if r["competitor"] == competitor]
                if len(competitor_records) >= 2:
                    old_price = competitor_records[0]["price"]
                    new_price = competitor_records[-1]["price"]
                    change_pct = (new_price - old_price) / old_price
                    
                    competitor_trends[competitor] = {
                        "old_price": old_price,
                        "new_price": new_price,
                        "change_percent": change_pct,
                        "trend": "increasing" if change_pct > 0.02 else "decreasing" if change_pct < -0.02 else "stable"
                    }
                    
                    # Flag significant changes
                    if abs(change_pct) >= self.price_change_threshold:
                        price_changes["significant_changes"].append({
                            "product_id": product_id,
                            "competitor": competitor,
                            "change_percent": change_pct,
                            "old_price": old_price,
                            "new_price": new_price,
                            "significance": "high" if abs(change_pct) > 0.1 else "medium"
                        })
            
            price_changes["trend_analysis"][product_id] = competitor_trends
        
        # Analyze our market position (simulate our prices)
        our_prices = {
            "PROD001": 99.99,
            "PROD002": 19.99,
            "PROD003": 79.99,
            "PROD004": 9.99,
            "PROD005": 39.99
        }
        
        for product_id, our_price in our_prices.items():
            competitor_prices = []
            for competitor, products in current_prices.items():
                if product_id in products:
                    competitor_prices.append(products[product_id]["price"])
            
            if competitor_prices:
                min_competitor_price = min(competitor_prices)
                max_competitor_price = max(competitor_prices)
                avg_competitor_price = np.mean(competitor_prices)
                
                position = "competitive"
                if our_price < min_competitor_price:
                    position = "below_market"
                elif our_price > max_competitor_price:
                    position = "above_market"
                
                price_changes["market_position"][product_id] = {
                    "our_price": our_price,
                    "min_competitor": min_competitor_price,
                    "max_competitor": max_competitor_price,
                    "avg_competitor": avg_competitor_price,
                    "position": position,
                    "price_gap_vs_min": our_price - min_competitor_price,
                    "price_gap_vs_avg": our_price - avg_competitor_price
                }
        
        self.logger.info(
            "Price change analysis complete",
            significant_changes=len(price_changes["significant_changes"]),
            products_analyzed=len(price_changes["market_position"])
        )
        
        return price_changes
    
    async def _analyze_market_trends(self) -> Dict[str, Any]:
        """Analyze overall market trends"""
        if len(self.price_history) < 20:
            return {"insufficient_data": True}
        
        # Analyze price volatility
        recent_records = self.price_history[-100:]
        
        # Group by product and calculate volatility
        product_volatility = {}
        for product_id in set(r["product_id"] for r in recent_records):
            product_records = [r for r in recent_records if r["product_id"] == product_id]
            prices = [r["price"] for r in product_records]
            
            if len(prices) > 1:
                volatility = np.std(prices) / np.mean(prices)  # Coefficient of variation
                product_volatility[product_id] = volatility
        
        # Identify market leaders (consistently lowest prices)
        market_leaders = {}
        for product_id in set(r["product_id"] for r in recent_records):
            competitor_avg_prices = {}
            for competitor in set(r["competitor"] for r in recent_records):
                competitor_product_records = [
                    r for r in recent_records 
                    if r["product_id"] == product_id and r["competitor"] == competitor
                ]
                if competitor_product_records:
                    avg_price = np.mean([r["price"] for r in competitor_product_records])
                    competitor_avg_prices[competitor] = avg_price
            
            if competitor_avg_prices:
                leader = min(competitor_avg_prices.items(), key=lambda x: x[1])
                market_leaders[product_id] = {
                    "leader": leader[0],
                    "avg_price": leader[1],
                    "price_advantage": max(competitor_avg_prices.values()) - leader[1]
                }
        
        # Analyze availability trends
        availability_analysis = {}
        for product_id in set(r["product_id"] for r in recent_records):
            product_records = [r for r in recent_records if r["product_id"] == product_id]
            
            total_records = len(product_records)
            in_stock_count = len([r for r in product_records if r.get("availability") == "in_stock"])
            low_stock_count = len([r for r in product_records if r.get("availability") == "low_stock"])
            out_of_stock_count = len([r for r in product_records if r.get("availability") == "out_of_stock"])
            
            availability_analysis[product_id] = {
                "in_stock_rate": in_stock_count / total_records,
                "low_stock_rate": low_stock_count / total_records,
                "out_of_stock_rate": out_of_stock_count / total_records,
                "availability_score": (in_stock_count + 0.5 * low_stock_count) / total_records
            }
        
        market_trends = {
            "price_volatility": product_volatility,
            "market_leaders": market_leaders,
            "availability_trends": availability_analysis,
            "overall_market_health": {
                "avg_volatility": np.mean(list(product_volatility.values())) if product_volatility else 0,
                "competitive_intensity": len(set(r["competitor"] for r in recent_records)),
                "avg_availability_score": np.mean([a["availability_score"] for a in availability_analysis.values()])
            }
        }
        
        self.logger.info("Market trend analysis complete")
        
        return market_trends
    
    async def _identify_pricing_opportunities(
        self,
        competitor_prices: Dict[str, Any],
        price_changes: Dict[str, Any],
        market_trends: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify pricing opportunities based on competitive analysis"""
        opportunities = []
        
        # Opportunity 1: Undercut competitors with high margins
        market_position = price_changes.get("market_position", {})
        for product_id, position_data in market_position.items():
            if position_data["position"] == "above_market":
                gap = position_data["price_gap_vs_min"]
                if gap > 5:  # $5 price gap
                    opportunities.append({
                        "type": "price_reduction",
                        "product_id": product_id,
                        "reason": "Price significantly above market",
                        "current_price": position_data["our_price"],
                        "recommended_price": position_data["min_competitor"] + 0.99,
                        "confidence": 0.8,
                        "potential_impact": "high",
                        "urgency": "high" if gap > 10 else "medium"
                    })
        
        # Opportunity 2: Premium pricing when we're market leader in availability
        availability_trends = market_trends.get("availability_trends", {})
        for product_id, availability_data in availability_trends.items():
            if availability_data["availability_score"] > 0.8:  # High availability
                position_data = market_position.get(product_id, {})
                if position_data and position_data["position"] in ["competitive", "below_market"]:
                    opportunities.append({
                        "type": "premium_pricing",
                        "product_id": product_id,
                        "reason": "High availability advantage",
                        "current_price": position_data["our_price"],
                        "recommended_price": position_data["our_price"] * 1.05,  # 5% increase
                        "confidence": 0.7,
                        "potential_impact": "medium",
                        "urgency": "low"
                    })
        
        # Opportunity 3: Quick response to competitor price changes
        significant_changes = price_changes.get("significant_changes", [])
        for change in significant_changes:
            if change["significance"] == "high":
                product_id = change["product_id"]
                position_data = market_position.get(product_id, {})
                
                if position_data:
                    if change["change_percent"] > 0:  # Competitor increased price
                        opportunities.append({
                            "type": "competitive_adjustment",
                            "product_id": product_id,
                            "reason": f"Competitor {change['competitor']} increased price by {change['change_percent']:.1%}",
                            "recommended_action": "Consider moderate price increase",
                            "confidence": 0.6,
                            "potential_impact": "medium",
                            "urgency": "medium"
                        })
                    else:  # Competitor decreased price
                        opportunities.append({
                            "type": "competitive_response",
                            "product_id": product_id,
                            "reason": f"Competitor {change['competitor']} decreased price by {abs(change['change_percent']):.1%}",
                            "recommended_action": "Consider matching or undercutting",
                            "confidence": 0.7,
                            "potential_impact": "high",
                            "urgency": "high"
                        })
        
        # Opportunity 4: Bundle opportunities with price-advantaged products
        for product_id, position_data in market_position.items():
            if position_data["position"] == "below_market":
                opportunities.append({
                    "type": "bundle_anchor",
                    "product_id": product_id,
                    "reason": "Price advantage makes this suitable as bundle anchor",
                    "recommended_action": "Use as primary item in bundles",
                    "confidence": 0.8,
                    "potential_impact": "high",
                    "urgency": "low"
                })
        
        self.logger.info(
            "Pricing opportunities identified",
            total_opportunities=len(opportunities)
        )
        
        return opportunities
    
    async def _share_pricing_insights(self, analysis: Dict[str, Any]) -> None:
        """Share pricing insights with other agents"""
        await self.communicator.publish(
            "competitor_price_update",
            analysis,
            self.name
        )
        
        self.logger.debug("Pricing insights shared")
    
    async def _generate_pricing_recommendations(self, opportunities: List[Dict[str, Any]]) -> None:
        """Generate and log pricing recommendations"""
        for opportunity in opportunities:
            recommendation = {
                "agent": self.name,
                "type": opportunity["type"],
                "product_id": opportunity.get("product_id"),
                "recommendation": opportunity.get("recommended_action", 
                                                f"Adjust price to {opportunity.get('recommended_price', 'TBD')}"),
                "confidence": opportunity["confidence"],
                "impact": opportunity["potential_impact"],
                "urgency": opportunity["urgency"],
                "reason": opportunity["reason"],
                "timestamp": datetime.now().isoformat()
            }
            
            await self.make_recommendation(recommendation)
    
    async def get_competitive_summary(self) -> Dict[str, Any]:
        """Get current competitive analysis summary for API responses"""
        if not self.competitor_data:
            await self._fetch_competitor_prices()
        
        # Calculate basic competitive metrics
        our_prices = {
            "PROD001": 99.99,
            "PROD002": 19.99,
            "PROD003": 79.99,
            "PROD004": 9.99,
            "PROD005": 39.99
        }
        
        competitive_metrics = {
            "below_market": 0,
            "competitive": 0,
            "above_market": 0
        }
        
        for product_id, our_price in our_prices.items():
            competitor_prices = []
            for competitor, products in self.competitor_data.items():
                if product_id in products:
                    competitor_prices.append(products[product_id]["price"])
            
            if competitor_prices:
                min_price = min(competitor_prices)
                max_price = max(competitor_prices)
                
                if our_price < min_price:
                    competitive_metrics["below_market"] += 1
                elif our_price > max_price:
                    competitive_metrics["above_market"] += 1
                else:
                    competitive_metrics["competitive"] += 1
        
        return {
            "competitors_monitored": len(self.competitor_data),
            "products_tracked": len(our_prices),
            "competitive_position": competitive_metrics,
            "price_history_records": len(self.price_history),
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "market_insights": {
                "price_volatility": "medium",  # Would be calculated from actual data
                "competitive_intensity": len(self.competitor_data),
                "data_freshness": "current"
            }
        }
