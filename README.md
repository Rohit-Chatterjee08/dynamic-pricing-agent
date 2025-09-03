# Auto-Bundler & Dynamic Pricing Agent

🤖 **Intelligent pricing and bundling optimization system** that monitors inventory, cart behavior, competitor pricing, and automatically creates dynamic bundles or discounts to maximize AOV through agentic logic.

## 🎯 What It Does

This system provides **on-the-fly optimization with no manual pricing strategy needed** by:

- **Inventory Monitoring**: Tracks stock levels, movement patterns, identifies slow-moving/high-demand products
- **Cart Behavior Analysis**: Analyzes abandonment patterns, frequently bought together items, user behavior signals  
- **Competitor Price Tracking**: Monitors competitor prices, tracks market trends, identifies pricing opportunities
- **Dynamic Bundling**: Creates intelligent product bundles based on inventory, behavior, and pricing data
- **Dynamic Pricing**: Adjusts prices in real-time based on demand, competition, and business objectives

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ FastAPI Server  │    │ Agent           │    │ Database        │
│ - REST API      │◄──►│ Orchestrator    │◄──►│ - SQLite/Postgres│
│ - Web Dashboard │    │ - Coordination  │    │ - Product Data  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
         ┌─────────────────┐  ┌─────────────────┐
         │ Specialized     │  │ ML Models       │
         │ Agents          │  │ - Demand Forecast│
         │ - Inventory     │  │ - Price Elasticity│
         │ - Cart Behavior │  │ - Bundle Scoring │
         │ - Competitor    │  └─────────────────┘
         │ - Bundler       │
         │ - Pricing       │
         └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis (optional, for advanced caching)

### Installation

1. **Clone and Setup**
```bash
git clone <repo-url>
cd auto_bundler_agent
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit configuration as needed
nano .env
```

3. **Run the System**
```bash
# Start the agent system
python main.py
```

4. **Access the Dashboard**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📊 Key Features

### 🔍 Inventory Monitoring Agent
- **Real-time stock tracking**: Monitors current levels vs. min/max thresholds
- **Movement pattern analysis**: Identifies fast/slow-moving products
- **Demand forecasting**: Predicts stock-outs and reorder needs
- **Optimization opportunities**: Recommends pricing/bundling strategies

### 🛒 Cart Behavior Analysis Agent
- **Abandonment pattern analysis**: Tracks cart abandonment triggers
- **Association rule mining**: Finds frequently bought together items
- **Price sensitivity analysis**: Identifies optimal price ranges
- **Seasonal pattern detection**: Adjusts for timing-based behavior

### 💰 Competitor Pricing Agent
- **Multi-source price monitoring**: Tracks competitor prices across platforms
- **Market position analysis**: Identifies above/below market positioning
- **Trend detection**: Monitors significant price changes
- **Competitive response**: Suggests pricing reactions

### 📦 Dynamic Bundler Agent
- **Multi-strategy bundling**: Association-based, inventory optimization, price-tier, complementary
- **Intelligent scoring**: Weights inventory impact, revenue potential, competitive advantage
- **Performance monitoring**: Tracks bundle conversion rates and revenue
- **Auto-optimization**: Creates/modifies bundles based on performance

### 🏷️ Dynamic Pricing Agent
- **Multi-factor pricing**: Considers demand, competition, inventory, elasticity
- **Strategy coordination**: Balances multiple pricing approaches
- **Constraint management**: Respects min/max prices and change limits
- **Impact tracking**: Monitors pricing decision outcomes

## 🎛️ Configuration

### Environment Variables

```bash
# Application Settings
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./auto_bundler.db

# Agent Intervals (seconds)
INVENTORY_MONITOR_INTERVAL=300
CART_BEHAVIOR_INTERVAL=600
COMPETITOR_PRICING_INTERVAL=900
DYNAMIC_BUNDLER_INTERVAL=1800
DYNAMIC_PRICING_INTERVAL=600

# Business Rules
LOW_STOCK_THRESHOLD=10
HIGH_STOCK_THRESHOLD=100
MAX_PRICE_INCREASE=0.20
MAX_PRICE_DECREASE=0.30
BUNDLE_CONFIDENCE_THRESHOLD=0.6
```

### Agent Configuration

Each agent can be individually configured:

```python
# Inventory thresholds
LOW_STOCK_THRESHOLD = 10
HIGH_STOCK_THRESHOLD = 100

# Bundling parameters
MIN_BUNDLE_SIZE = 2
MAX_BUNDLE_SIZE = 4
MIN_BUNDLE_DISCOUNT = 0.05
MAX_BUNDLE_DISCOUNT = 0.25

# Pricing constraints
MAX_PRICE_INCREASE = 0.20
MAX_PRICE_DECREASE = 0.30
PRICE_CHANGE_THRESHOLD = 0.02
```

## 🔌 API Endpoints

### System Status
```http
GET /api/v1/status
GET /api/v1/agents
GET /api/v1/agents/{agent_name}
```

### Product Management
```http
GET /api/v1/products
GET /api/v1/products/{product_id}
POST /api/v1/products/{product_id}/price
```

### Recommendations
```http
GET /api/v1/recommendations
PUT /api/v1/recommendations/{id}/status
```

### Bundles
```http
GET /api/v1/bundles
```

### Analytics
```http
GET /api/v1/analytics/summary
```

## 💻 API Examples

### Get System Status
```bash
curl http://localhost:8000/api/v1/status
```

### Get All Products
```bash
curl http://localhost:8000/api/v1/products
```

### Change Product Price
```bash
curl -X POST http://localhost:8000/api/v1/products/PROD001/price \
  -H "Content-Type: application/json" \
  -d '{"new_price": 89.99, "reason": "Competitor price match"}'
```

### Get Recommendations
```bash
curl http://localhost:8000/api/v1/recommendations?status=pending
```

## 📈 Sample Output

### Agent Recommendations
```json
{
  "id": 1,
  "agent_name": "dynamic_pricing",
  "type": "price_change_executed",
  "product_id": "PROD001",
  "recommendation": "Changed price from $99.99 to $94.99",
  "confidence": 0.85,
  "impact": "medium",
  "urgency": "high",
  "timestamp": "2025-01-03T10:30:00Z"
}
```

### Bundle Creation
```json
{
  "bundle_id": "bundle_20250103_103045_1234",
  "name": "Wireless Audio Bundle",
  "items": ["PROD001", "PROD003"],
  "individual_price": 179.98,
  "bundle_price": 159.98,
  "discount_percent": 11.1,
  "strategy": "association_based",
  "confidence": 0.75
}
```

### System Analytics
```json
{
  "summary": {
    "total_products": 5,
    "active_bundles": 3,
    "recent_price_changes": 7,
    "pending_recommendations": 12
  },
  "agent_summaries": {
    "inventory_monitor": {
      "low_stock_items": 2,
      "high_stock_items": 1,
      "total_inventory_value": 12450.50
    }
  }
}
```

## 🧠 Machine Learning Integration

The system supports ML models for:

- **Demand Forecasting**: Predict future demand patterns
- **Price Elasticity**: Analyze price sensitivity
- **Bundle Scoring**: Optimize bundle recommendations
- **Customer Segmentation**: Personalize pricing strategies

## 🔄 Agent Coordination

Agents work together through:

1. **Message Passing**: Share insights via event-driven communication
2. **Coordinated Optimization**: Cross-agent decision making
3. **Conflict Resolution**: Handle competing recommendations
4. **Performance Feedback**: Learn from outcome data

## 🛡️ Safety & Constraints

- **Price Boundaries**: Configurable min/max price limits
- **Change Limits**: Maximum percentage changes per period
- **Confidence Thresholds**: Only high-confidence changes auto-applied
- **Manual Overrides**: Human review for critical decisions
- **Rollback Capability**: Undo problematic changes

## 📝 Monitoring & Alerting

- **Real-time Dashboards**: Web interface for system monitoring
- **Performance Metrics**: Track agent effectiveness
- **Alert System**: Notifications for critical events
- **Audit Trails**: Complete history of all decisions

## 🔧 Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Development Setup
```bash
# Set development environment
export ENVIRONMENT=development

# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Use faster intervals for testing
export INVENTORY_MONITOR_INTERVAL=60
export DYNAMIC_PRICING_INTERVAL=120
```

## 🏭 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Environment-Specific Settings
- **Development**: Fast intervals, debug logging
- **Staging**: Production-like with safety limits
- **Production**: Conservative intervals, monitoring enabled

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Health Check**: `/health` endpoint
- **Logs**: Check application logs for troubleshooting

## 🗺️ Roadmap

- [ ] Advanced ML model integration
- [ ] Multi-currency support
- [ ] A/B testing framework
- [ ] Advanced alerting system
- [ ] Mobile app integration
- [ ] Kubernetes deployment manifests

---

**Built with ❤️ for intelligent e-commerce optimization**
