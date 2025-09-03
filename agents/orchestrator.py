"""
Agent Orchestrator for coordinating all agents in the Auto-Bundler & Dynamic Pricing system.
Manages agent lifecycle, communication, and coordination.
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime

import structlog

from .base import BaseAgent, AgentCommunicator
from .inventory_monitor import InventoryMonitorAgent
from .cart_behavior import CartBehaviorAgent
from .competitor_pricing import CompetitorPricingAgent
from .dynamic_bundler import DynamicBundlerAgent
from .dynamic_pricing import DynamicPricingAgent


class AgentOrchestrator:
    """
    Orchestrates all agents in the system.
    Handles initialization, lifecycle management, and inter-agent communication.
    """
    
    def __init__(self, settings: Any, db_manager: Any):
        self.settings = settings
        self.db_manager = db_manager
        self.logger = structlog.get_logger(component="orchestrator")
        
        # Agent communication
        self.communicator = AgentCommunicator()
        
        # Initialize all agents
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
    
    def _initialize_agents(self) -> None:
        """Initialize all specialized agents"""
        agent_classes = {
            "inventory_monitor": InventoryMonitorAgent,
            "cart_behavior": CartBehaviorAgent,
            "competitor_pricing": CompetitorPricingAgent,
            "dynamic_bundler": DynamicBundlerAgent,
            "dynamic_pricing": DynamicPricingAgent
        }
        
        for agent_name, agent_class in agent_classes.items():
            try:
                self.agents[agent_name] = agent_class(
                    name=agent_name,
                    settings=self.settings,
                    db_manager=self.db_manager,
                    communicator=self.communicator
                )
                self.logger.info(f"Initialized {agent_name} agent")
            except Exception as e:
                self.logger.error(
                    f"Failed to initialize {agent_name} agent",
                    error=str(e),
                    exc_info=True
                )
    
    async def initialize(self) -> None:
        """Initialize all agents and setup communication"""
        self.logger.info("Initializing agent orchestrator")
        
        # Initialize each agent
        for agent_name, agent in self.agents.items():
            try:
                await agent.initialize()
                self.logger.info(f"Agent {agent_name} initialized successfully")
            except Exception as e:
                self.logger.error(
                    f"Failed to initialize agent {agent_name}",
                    error=str(e),
                    exc_info=True
                )
        
        # Setup agent communication patterns
        await self._setup_communication()
        
        self.logger.info("Agent orchestrator initialization complete")
    
    async def _setup_communication(self) -> None:
        """Setup communication channels between agents"""
        # Inventory data sharing
        await self.communicator.subscribe(
            "inventory_update",
            self._handle_inventory_update
        )
        
        # Cart behavior insights
        await self.communicator.subscribe(
            "cart_behavior_insight",
            self._handle_cart_behavior_insight
        )
        
        # Competitor pricing updates
        await self.communicator.subscribe(
            "competitor_price_update",
            self._handle_competitor_price_update
        )
        
        # Bundle recommendations
        await self.communicator.subscribe(
            "bundle_recommendation",
            self._handle_bundle_recommendation
        )
        
        # Price change recommendations
        await self.communicator.subscribe(
            "price_change_recommendation",
            self._handle_price_change_recommendation
        )
    
    async def start_background_tasks(self) -> None:
        """Start all background agent tasks"""
        self.logger.info("Starting background agent tasks")
        
        # Start message processor
        message_task = asyncio.create_task(
            self.communicator.start_message_processor()
        )
        self._background_tasks.append(message_task)
        
        # Start all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.start()
                self.logger.info(f"Started agent {agent_name}")
            except Exception as e:
                self.logger.error(
                    f"Failed to start agent {agent_name}",
                    error=str(e),
                    exc_info=True
                )
        
        # Start coordination task
        coordination_task = asyncio.create_task(self._coordination_loop())
        self._background_tasks.append(coordination_task)
        
        self.logger.info("All background tasks started")
    
    async def _coordination_loop(self) -> None:
        """Main coordination loop for cross-agent optimization"""
        while True:
            try:
                await asyncio.sleep(self.settings.COORDINATION_INTERVAL)
                await self._run_coordination_cycle()
            except Exception as e:
                self.logger.error(
                    "Coordination cycle error",
                    error=str(e),
                    exc_info=True
                )
    
    async def _run_coordination_cycle(self) -> None:
        """Run a coordination cycle to optimize across all agents"""
        self.logger.info("Running coordination cycle")
        
        # Collect current state from all agents
        current_state = {}
        for agent_name, agent in self.agents.items():
            try:
                status = await agent.get_status()
                current_state[agent_name] = status
            except Exception as e:
                self.logger.error(
                    f"Failed to get status from {agent_name}",
                    error=str(e)
                )
        
        # Analyze system-wide optimization opportunities
        optimizations = await self._analyze_optimization_opportunities(current_state)
        
        # Execute coordinated optimizations
        if optimizations:
            await self._execute_coordinated_optimizations(optimizations)
    
    async def _analyze_optimization_opportunities(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze cross-agent optimization opportunities"""
        optimizations = []
        
        # Example: If inventory is high and competitor prices are lower,
        # recommend aggressive pricing and bundling
        inventory_agent_status = state.get("inventory_monitor", {})
        competitor_agent_status = state.get("competitor_pricing", {})
        
        # This would contain sophisticated logic to identify optimization opportunities
        # For now, we'll implement basic coordination rules
        
        self.logger.debug("Analyzing optimization opportunities", state=state)
        
        return optimizations
    
    async def _execute_coordinated_optimizations(self, optimizations: List[Dict[str, Any]]) -> None:
        """Execute coordinated optimizations across multiple agents"""
        for optimization in optimizations:
            self.logger.info("Executing optimization", optimization=optimization)
            # Implementation would depend on the specific optimization
    
    # Message handlers for inter-agent communication
    
    async def _handle_inventory_update(self, message: Dict[str, Any]) -> None:
        """Handle inventory updates from inventory monitor agent"""
        inventory_data = message["message"]
        self.logger.debug("Processing inventory update", data=inventory_data)
        
        # Notify relevant agents about inventory changes
        if "low_stock_items" in inventory_data:
            await self.communicator.publish(
                "low_stock_alert",
                inventory_data,
                "orchestrator"
            )
    
    async def _handle_cart_behavior_insight(self, message: Dict[str, Any]) -> None:
        """Handle cart behavior insights"""
        behavior_data = message["message"]
        self.logger.debug("Processing cart behavior insight", data=behavior_data)
        
        # Share insights with bundling and pricing agents
        await self.communicator.publish(
            "behavior_insight_shared",
            behavior_data,
            "orchestrator"
        )
    
    async def _handle_competitor_price_update(self, message: Dict[str, Any]) -> None:
        """Handle competitor price updates"""
        pricing_data = message["message"]
        self.logger.debug("Processing competitor price update", data=pricing_data)
        
        # Share with dynamic pricing agent for immediate response
        await self.communicator.publish(
            "competitor_price_shared",
            pricing_data,
            "orchestrator"
        )
    
    async def _handle_bundle_recommendation(self, message: Dict[str, Any]) -> None:
        """Handle bundle recommendations from dynamic bundler"""
        bundle_data = message["message"]
        self.logger.info("Processing bundle recommendation", data=bundle_data)
        
        # Log and potentially auto-apply bundle recommendations
        if bundle_data.get("confidence", 0) > self.settings.AUTO_APPLY_BUNDLE_THRESHOLD:
            await self._auto_apply_bundle(bundle_data)
    
    async def _handle_price_change_recommendation(self, message: Dict[str, Any]) -> None:
        """Handle price change recommendations from dynamic pricing agent"""
        price_data = message["message"]
        self.logger.info("Processing price change recommendation", data=price_data)
        
        # Log and potentially auto-apply price changes
        if price_data.get("confidence", 0) > self.settings.AUTO_APPLY_PRICE_THRESHOLD:
            await self._auto_apply_price_change(price_data)
    
    async def _auto_apply_bundle(self, bundle_data: Dict[str, Any]) -> None:
        """Automatically apply high-confidence bundle recommendations"""
        try:
            # Implementation would integrate with your e-commerce platform
            self.logger.info("Auto-applying bundle", bundle=bundle_data)
            # await self.db_manager.create_bundle(bundle_data)
        except Exception as e:
            self.logger.error("Failed to auto-apply bundle", error=str(e))
    
    async def _auto_apply_price_change(self, price_data: Dict[str, Any]) -> None:
        """Automatically apply high-confidence price changes"""
        try:
            # Implementation would integrate with your e-commerce platform
            self.logger.info("Auto-applying price change", price_change=price_data)
            # await self.db_manager.update_pricing(price_data)
        except Exception as e:
            self.logger.error("Failed to auto-apply price change", error=str(e))
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "system_metrics": {
                "active_agents": len([a for a in self.agents.values() if a.enabled]),
                "total_agents": len(self.agents),
                "background_tasks": len(self._background_tasks)
            }
        }
        
        # Get status from each agent
        for agent_name, agent in self.agents.items():
            try:
                status["agents"][agent_name] = await agent.get_status()
            except Exception as e:
                status["agents"][agent_name] = {
                    "error": str(e),
                    "status": "error"
                }
        
        return status
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all agents and tasks"""
        self.logger.info("Shutting down agent orchestrator")
        
        # Stop all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.stop()
                self.logger.info(f"Stopped agent {agent_name}")
            except Exception as e:
                self.logger.error(
                    f"Error stopping agent {agent_name}",
                    error=str(e)
                )
        
        # Cancel background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("Agent orchestrator shutdown complete")
