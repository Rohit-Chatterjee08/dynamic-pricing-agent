"""
Base Agent class for the Auto-Bundler & Dynamic Pricing system.
All specialized agents inherit from this base class.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import structlog


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    total_recommendations: int = 0
    accepted_recommendations: int = 0


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    Provides common functionality like logging, metrics, and execution framework.
    """
    
    def __init__(self, name: str, settings: Any, db_manager: Any):
        self.name = name
        self.settings = settings
        self.db_manager = db_manager
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        
        # Setup structured logging
        self.logger = structlog.get_logger(agent=name)
        
        # Configuration
        self.execution_interval = getattr(settings, f"{name.upper()}_INTERVAL", 300)  # 5 minutes default
        self.enabled = getattr(settings, f"{name.upper()}_ENABLED", True)
        
        # Internal state
        self._task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize the agent. Override in subclasses for custom initialization."""
        self.logger.info("Agent initialized", agent=self.name)
    
    async def start(self) -> None:
        """Start the agent's background task"""
        if not self.enabled:
            self.logger.info("Agent is disabled, not starting", agent=self.name)
            return
            
        if self._task and not self._task.done():
            self.logger.warning("Agent already running", agent=self.name)
            return
            
        self._task = asyncio.create_task(self._run_loop())
        self.logger.info("Agent started", agent=self.name)
    
    async def stop(self) -> None:
        """Stop the agent's background task"""
        self._shutdown_event.set()
        
        if self._task:
            await self._task
            
        self.logger.info("Agent stopped", agent=self.name)
    
    async def _run_loop(self) -> None:
        """Main execution loop for the agent"""
        self.logger.info("Starting agent execution loop", interval=self.execution_interval)
        
        while not self._shutdown_event.is_set():
            try:
                self.status = AgentStatus.RUNNING
                start_time = datetime.now()
                
                # Execute the agent's main logic
                await self.execute()
                
                # Update metrics
                self.metrics.executions += 1
                self.metrics.successful_executions += 1
                self.metrics.last_execution = start_time
                
                execution_time = (datetime.now() - start_time).total_seconds()
                self.metrics.avg_execution_time = (
                    (self.metrics.avg_execution_time * (self.metrics.executions - 1) + execution_time)
                    / self.metrics.executions
                )
                
                self.status = AgentStatus.IDLE
                self.logger.info(
                    "Agent execution completed",
                    execution_time=execution_time,
                    total_executions=self.metrics.executions
                )
                
            except Exception as e:
                self.status = AgentStatus.ERROR
                self.metrics.failed_executions += 1
                self.logger.error(
                    "Agent execution failed",
                    error=str(e),
                    exc_info=True
                )
            
            # Wait for next execution or shutdown
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.execution_interval
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Time for next execution
    
    @abstractmethod
    async def execute(self) -> None:
        """
        Main execution logic for the agent.
        Must be implemented by all subclasses.
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "name": self.name,
            "status": self.status.value,
            "enabled": self.enabled,
            "metrics": {
                "executions": self.metrics.executions,
                "successful_executions": self.metrics.successful_executions,
                "failed_executions": self.metrics.failed_executions,
                "success_rate": (
                    self.metrics.successful_executions / max(self.metrics.executions, 1)
                ),
                "avg_execution_time": self.metrics.avg_execution_time,
                "last_execution": self.metrics.last_execution.isoformat() if self.metrics.last_execution else None,
                "total_recommendations": self.metrics.total_recommendations,
                "accepted_recommendations": self.metrics.accepted_recommendations,
                "acceptance_rate": (
                    self.metrics.accepted_recommendations / max(self.metrics.total_recommendations, 1)
                )
            }
        }
    
    async def make_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """
        Make a recommendation to the system.
        Logs the recommendation and updates metrics.
        """
        self.metrics.total_recommendations += 1
        
        self.logger.info(
            "Agent recommendation",
            recommendation=recommendation,
            agent=self.name
        )
        
        # Store recommendation in database for tracking
        await self._store_recommendation(recommendation)
    
    async def _store_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """Store recommendation in database for tracking and analysis"""
        try:
            # This would be implemented based on your database schema
            # For now, we'll just log it
            self.logger.debug("Storing recommendation", recommendation=recommendation)
        except Exception as e:
            self.logger.error("Failed to store recommendation", error=str(e))


class AgentCommunicator:
    """
    Facilitates communication between agents.
    Allows agents to share data and coordinate actions.
    """
    
    def __init__(self):
        self._message_queue = asyncio.Queue()
        self._subscribers = {}
    
    async def publish(self, topic: str, message: Dict[str, Any], sender: str) -> None:
        """Publish a message to a topic"""
        await self._message_queue.put({
            "topic": topic,
            "message": message,
            "sender": sender,
            "timestamp": datetime.now()
        })
    
    async def subscribe(self, topic: str, callback) -> None:
        """Subscribe to a topic"""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
    
    async def start_message_processor(self) -> None:
        """Start processing messages from the queue"""
        while True:
            try:
                message = await self._message_queue.get()
                topic = message["topic"]
                
                if topic in self._subscribers:
                    for callback in self._subscribers[topic]:
                        try:
                            await callback(message)
                        except Exception as e:
                            structlog.get_logger().error(
                                "Message processing error",
                                topic=topic,
                                error=str(e)
                            )
                            
            except Exception as e:
                structlog.get_logger().error("Message queue error", error=str(e))
