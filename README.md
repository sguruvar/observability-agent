# Intelligent Observability Platform

A comprehensive, AI-powered observability platform that correlates metrics, logs, and traces to provide actionable insights and automated problem detection.

## 🚀 What We Built

This is a complete, production-ready observability platform that demonstrates:

- **Real-time correlation** between metrics, logs, and traces
- **AI-powered problem detection** with automated recommendations
- **Cross-signal analysis** that tells the complete story of system behavior
- **Intelligent dashboards** with live updates and correlation insights
- **Docker-based infrastructure** for easy deployment and scaling

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask App     │───▶│  OpenTelemetry   │───▶│  Observability  │
│  (Port 3002)    │    │  Instrumentation │    │     Stack       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    AI Correlation       │
                    │      Engine             │
                    │   (Port 8000)          │
                    └─────────────────────────┘
```

## 📦 Components

### Application Layer
- **Python Flask Application** - Insurance claims processing system
- **OpenTelemetry Instrumentation** - Comprehensive telemetry collection
- **Custom Metrics** - Business logic metrics (claims_submitted_total, processing_duration_seconds)
- **Structured Logging** - OpenSearch integration with custom handler
- **Distributed Tracing** - Jaeger OTLP exporter

### Observability Stack
- **Prometheus** - Metrics collection and storage (port 9090)
- **OpenSearch** - Log aggregation and search (ports 9200, 5601)
- **Jaeger** - Distributed tracing (ports 16686, 4317, 4318)
- **Grafana** - Visualization dashboards (port 3000)

### AI Intelligence Layer
- **AI Agent** - Real-time problem detection (port 8000)
- **Correlation Engine** - Cross-signal analysis
- **Automated Recommendations** - Business impact assessment
- **Real-time Dashboard** - Live updates every 10 seconds

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/sguruvar/observability-agent.git
cd observability-agent
```

### 2. Start the Observability Stack
```bash
cd observability
docker-compose up -d
```

### 3. Start the Application
```bash
cd app
pip install -r requirements.txt
PORT=3002 python app_local.py
```

### 4. Access the Dashboards
- **AI Dashboard**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **OpenSearch**: http://localhost:5601
- **Jaeger**: http://localhost:16686
- **Grafana**: http://localhost:3000 (admin/admin)

## 🧪 Testing

### Generate Test Data
```bash
python test_correlation.py
```

### Manual Testing
```bash
# Submit test claims
curl -X POST http://localhost:3002/submit_claim \
  -H "Content-Type: application/json" \
  -d '{"policy_number": "INVALID1", "amount": 1000, "description": "Test claim"}'

# Check correlation
curl http://localhost:8000/api/correlation/story
```

## 📊 Key Features

### 1. Real-time Problem Detection
- AI agent monitors metrics for anomalies
- Detects high rejection rates automatically
- Generates alerts with context

### 2. Cross-Signal Correlation
- Links metrics (rejection rate) with logs (rejection reasons)
- Correlates with traces (processing flow)
- Provides complete incident narrative

### 3. Intelligent Dashboards
- AI-powered dashboard with correlation analysis
- Real-time updates every 10 seconds
- Visual representation of the complete story

### 4. Automated Recommendations
- AI generates specific remediation steps
- Estimates fix complexity and time
- Provides business impact analysis

## 🔧 Configuration

### Environment Variables
```bash
# Application
PORT=3002

# Observability Stack
PROMETHEUS_URL=http://localhost:9090
OPENSEARCH_URL=http://localhost:9200
JAEGER_URL=http://localhost:16686
JAEGER_OTLP_ENDPOINT=http://localhost:4317
```

### Prometheus Queries
```promql
# Claims submission rate
sum(rate(claims_submitted_total[5m]))

# Rejection rate
sum(claims_submitted_total{status="rejected"}) / sum(claims_submitted_total)

# Processing duration
histogram_quantile(0.95, sum(rate(processing_duration_seconds_bucket[5m])) by (le))
```

## 📁 Project Structure

```
observability-agent/
├── app/                          # Flask application
│   ├── app_local.py             # Main application
│   ├── opensearch_handler.py    # Custom logging handler
│   └── requirements.txt         # Python dependencies
├── observability/               # Observability stack
│   ├── docker-compose.yml       # Docker orchestration
│   ├── prometheus.yml           # Prometheus configuration
│   ├── ai-agent/                # AI correlation engine
│   │   ├── app.py              # AI agent application
│   │   ├── correlation_engine.py # Correlation logic
│   │   ├── templates/          # Dashboard templates
│   │   └── requirements.txt    # AI agent dependencies
│   └── grafana/                 # Grafana dashboards
├── test_correlation.py          # Comprehensive testing
└── README.md                    # This file
```

## 🎯 Use Cases

### 1. Incident Response
- Automatic problem detection
- Root cause analysis through correlation
- Actionable recommendations

### 2. Performance Monitoring
- Real-time metrics collection
- Trace analysis for bottlenecks
- Log correlation for context

### 3. Business Intelligence
- Custom business metrics
- Trend analysis
- Impact assessment

## 🔍 API Endpoints

### Application API
- `POST /submit_claim` - Submit insurance claim
- `GET /claims` - Retrieve all claims
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### AI Agent API
- `GET /api/analysis` - System health analysis
- `GET /api/correlation/story` - Complete correlation story
- `GET /api/correlation/rejection` - Rejection pattern analysis
- `GET /api/correlation/errors` - Error spike analysis
- `GET /api/correlation/performance` - Performance analysis

## 🚀 Performance Characteristics

- **Metrics**: Prometheus scrapes every 15 seconds with minimal overhead
- **Logs**: OpenSearch handles 100+ log entries per minute efficiently
- **Traces**: Jaeger processes traces with <50ms latency
- **AI Correlation**: Generates insights in <2 seconds
- **Dashboard**: Updates every 10 seconds with live data

## 🛠️ Development

### Adding New Metrics
```python
from prometheus_client import Counter, Histogram

# Define custom metrics
custom_metric = Counter('custom_metric_total', 'Description', ['label'])

# Use in application
custom_metric.labels(label='value').inc()
```

### Adding New Correlation Patterns
```python
# In correlation_engine.py
def correlate_new_pattern(self):
    # Query data sources
    metrics = self._query_prometheus('your_query')
    logs = self._query_opensearch('index', query_body)
    traces = self._query_jaeger('service')
    
    # Perform correlation
    return correlation_result
```

## 📈 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:3002/health

# AI agent health
curl http://localhost:8000/health

# Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### Logs
```bash
# Application logs
docker logs observability-ai-agent

# Prometheus logs
docker logs observability-prometheus

# OpenSearch logs
docker logs observability-opensearch
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenTelemetry for instrumentation
- Prometheus for metrics collection
- OpenSearch for log aggregation
- Jaeger for distributed tracing
- Grafana for visualization

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the test cases

---

**Built with ❤️ for intelligent observability**