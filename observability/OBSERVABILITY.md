# 🔍 Observability Stack - Minimal Setup

A minimal observability platform using Prometheus, OpenSearch, Jaeger, and AI-powered problem detection.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │───►│   Prometheus    │    │   OpenSearch    │
│   (Instrumented)│    │   (Metrics)     │    │   (Logs)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Jaeger      │
                    │   (Tracing)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   AI Agent      │
                    │ (Problem Det.)  │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Observability Stack

```bash
# Start all services
python start_observability.py

# Or manually
docker-compose up -d
```

### 2. Start Your Instrumented App

```bash
# Install dependencies
pip install -r requirements.txt

# Start the instrumented Flask app
python app_instrumented.py
```

### 3. Access the Dashboards

- **AI Agent Dashboard**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **OpenSearch**: http://localhost:9200
- **OpenSearch Dashboards**: http://localhost:5601
- **Jaeger**: http://localhost:16686
- **Grafana**: http://localhost:3001 (admin/admin)

## 📊 What You Get

### **Metrics (Prometheus)**
- HTTP request count, duration, error rate
- Custom business metrics
- System resource usage

### **Logs (OpenSearch)**
- Application logs with structured data
- Error logs and stack traces
- Request/response logs

### **Traces (Jaeger)**
- Request flow across services
- Database operations
- External API calls
- Performance bottlenecks

### **AI Problem Detection**
- Automatic anomaly detection
- Root cause analysis
- Actionable recommendations
- Real-time alerts

## 🔧 Configuration

### Environment Variables

```env
# Observability
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=14268
OTLP_ENDPOINT=http://localhost:4317

# Your app
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket
# ... other app config
```

### Prometheus Queries

```promql
# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Request rate
rate(http_requests_total[5m])
```

## 🛠️ Development

### Adding Custom Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Custom metrics
CLAIM_SUBMISSIONS = Counter('claims_submitted_total', 'Total claims submitted')
CLAIM_PROCESSING_TIME = Histogram('claim_processing_seconds', 'Time to process claims')
ACTIVE_CLAIMS = Gauge('active_claims', 'Number of active claims')

# Use in your code
CLAIM_SUBMISSIONS.inc()
with CLAIM_PROCESSING_TIME.time():
    # process claim
    pass
```

### Adding Custom Traces

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route('/api/claims')
def get_claims():
    with tracer.start_as_current_span("get_claims") as span:
        span.set_attribute("user.id", user_id)
        # your code here
```

### Adding Custom Logs

```python
import logging

logger = logging.getLogger(__name__)

# Structured logging
logger.info("Claim submitted", extra={
    "claim_id": claim_id,
    "user_id": user_id,
    "amount": amount
})
```

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

### No Data in Dashboards

1. **Check if app is instrumented**: Visit http://localhost:3000/metrics
2. **Check Prometheus targets**: http://localhost:9090/targets
3. **Check OpenSearch indices**: http://localhost:9200/_cat/indices
4. **Check Jaeger services**: http://localhost:16686

### Performance Issues

```bash
# Check resource usage
docker stats

# Scale down if needed
docker-compose down
# Edit docker-compose.yml to reduce resources
docker-compose up -d
```

## 📈 Monitoring Your App

### Key Metrics to Watch

1. **Error Rate**: Should be < 1%
2. **Response Time P95**: Should be < 2s
3. **Memory Usage**: Should be < 80%
4. **Request Rate**: Monitor for spikes

### Alerts to Set Up

1. **High Error Rate**: > 5% for 5 minutes
2. **Slow Response Time**: P95 > 5s for 5 minutes
3. **High Memory Usage**: > 90% for 5 minutes
4. **No Requests**: 0 requests for 10 minutes

## 🔄 Stopping the Stack

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## 📚 Next Steps

1. **Add more custom metrics** for your business logic
2. **Set up alerting** with Prometheus AlertManager
3. **Create custom dashboards** in Grafana
4. **Add more AI analysis** patterns
5. **Integrate with external monitoring** tools

## 🤝 Contributing

Feel free to add more observability features:
- More AI problem detection patterns
- Custom Grafana dashboards
- Additional metrics and traces
- Better alerting rules
