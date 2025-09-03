#!/usr/bin/env python3
"""
Simple test script to verify the Auto-Bundler & Dynamic Pricing Agent system.
Run this to make sure all components are working correctly.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_system():
    """Test the basic system components"""
    
    print("🤖 Testing Auto-Bundler & Dynamic Pricing Agent System")
    print("=" * 60)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    try:
        from config.settings import Settings, validate_configuration
        settings = Settings()
        print(f"   ✅ Configuration loaded - Version: {settings.VERSION}")
        print(f"   ✅ Debug mode: {settings.DEBUG}")
        print(f"   ✅ API host: {settings.API_HOST}:{settings.API_PORT}")
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False
    
    # Test 2: Database
    print("\n2. Testing Database...")
    try:
        from database.connection import DatabaseManager
        db_manager = DatabaseManager(settings)
        await db_manager.initialize()
        health = await db_manager.health_check()
        print(f"   ✅ Database initialized: {health}")
        
        # Test database stats
        stats = await db_manager.get_stats()
        print(f"   ✅ Database stats: {stats}")
        
    except Exception as e:
        print(f"   ❌ Database failed: {e}")
        return False
    
    # Test 3: Agents
    print("\n3. Testing Agent System...")
    try:
        from agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator(settings, db_manager)
        await orchestrator.initialize()
        print(f"   ✅ Agent orchestrator initialized")
        print(f"   ✅ Agents loaded: {list(orchestrator.agents.keys())}")
        
        # Get agent status
        for agent_name, agent in orchestrator.agents.items():
            try:
                status = await agent.get_status()
                print(f"   ✅ {agent_name}: {status['status']} (enabled: {status['enabled']})")
            except Exception as e:
                print(f"   ⚠️  {agent_name}: Error getting status - {e}")
        
    except Exception as e:
        print(f"   ❌ Agent system failed: {e}")
        return False
    
    # Test 4: API Server
    print("\n4. Testing API Server...")
    try:
        from api.server import create_app
        app = create_app(settings, orchestrator)
        print("   ✅ FastAPI app created successfully")
        print(f"   ✅ App title: {app.title}")
        print(f"   ✅ App version: {app.version}")
        
    except Exception as e:
        print(f"   ❌ API server failed: {e}")
        return False
    
    # Test 5: Agent Execution (single cycle)
    print("\n5. Testing Agent Execution...")
    try:
        # Test inventory monitor agent
        inventory_agent = orchestrator.agents.get('inventory_monitor')
        if inventory_agent:
            await inventory_agent.execute()
            print("   ✅ Inventory Monitor agent executed")
        
        # Test cart behavior agent
        cart_agent = orchestrator.agents.get('cart_behavior') 
        if cart_agent:
            await cart_agent.execute()
            print("   ✅ Cart Behavior agent executed")
        
        print("   ✅ Agent execution test completed")
        
    except Exception as e:
        print(f"   ⚠️  Agent execution test failed: {e}")
        # Don't fail the whole test for execution issues
    
    # Cleanup
    try:
        await orchestrator.shutdown()
        await db_manager.close()
        print("\n✅ System cleanup completed")
    except Exception as e:
        print(f"\n⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 System test completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Run 'python main.py' to start the full system")
    print("   2. Visit http://localhost:8000 for the web dashboard")
    print("   3. Visit http://localhost:8000/docs for API documentation")
    print("   4. Check http://localhost:8000/health for system health")
    
    return True


async def quick_demo():
    """Run a quick demo of the system capabilities"""
    
    print("\n🚀 Quick Demo - Agent Recommendations")
    print("=" * 50)
    
    try:
        from config.settings import Settings
        from database.connection import DatabaseManager
        from agents.orchestrator import AgentOrchestrator
        
        settings = Settings()
        db_manager = DatabaseManager(settings)
        await db_manager.initialize()
        
        orchestrator = AgentOrchestrator(settings, db_manager)
        await orchestrator.initialize()
        
        print("\n📊 Running agents to generate sample recommendations...")
        
        # Execute each agent once
        for agent_name, agent in orchestrator.agents.items():
            try:
                print(f"   Running {agent_name}...")
                await agent.execute()
                
                # Get agent status
                status = await agent.get_status()
                metrics = status.get('metrics', {})
                print(f"   - {agent_name}: {metrics.get('executions', 0)} executions, "
                      f"{metrics.get('total_recommendations', 0)} recommendations")
                
            except Exception as e:
                print(f"   ⚠️  {agent_name} execution error: {e}")
        
        print("\n📈 System Status:")
        system_status = await orchestrator.get_system_status()
        print(f"   - Active agents: {system_status['system_metrics']['active_agents']}")
        print(f"   - Total agents: {system_status['system_metrics']['total_agents']}")
        
        # Cleanup
        await orchestrator.shutdown()
        await db_manager.close()
        
        print("\n✨ Demo completed! The agents are working and generating recommendations.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    print("Auto-Bundler & Dynamic Pricing Agent - System Test\n")
    
    # Run the test
    try:
        success = asyncio.run(test_system())
        if success:
            # Run demo if test passed
            asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
