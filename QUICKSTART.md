# 🚀 Quick Start Guide - Local Development

## What's Running

Your complete observability stack is now running locally without any AWS dependencies!

### ✅ Services Running:

1. **Insurance Claims App** (Port 3002)
   - Local in-memory processing
   - Full OpenTelemetry instrumentation
   - No AWS services required

2. **Observability Stack** (Docker):
   - Prometheus (Port 9090) - Metrics
   - OpenSearch (Port 9200) - Logs
   - Jaeger (Port 16686) - Tracing
   - AI Agent (Port 8000) - Problem Detection
   - Grafana (Port 3001) - Dashboards

## 🌐 Access URLs

- **Main App**: http://localhost:3002
- **AI Dashboard**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Jaeger UI**: http://localhost:16686
- **OpenSearch**: http://localhost:5601
- **Grafana**: http://localhost:3001 (admin/admin)

## 📋 Test the System

### 1. Submit a Claim (via API)

```bash
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL001" \
  -F "claimType=auto" \
  -F "description=Car accident" \
  -F "amount=2500" \
  -F "contactEmail=test@example.com" \
  -F "contactPhone=555-1234"
```

### 2. Check Claim Status

```bash
curl http://localhost:3002/api/claims/{CLAIM_ID}
```

### 3. View All Claims

```bash
curl http://localhost:3002/api/claims
```

### 4. Check Metrics

```bash
curl http://localhost:3002/metrics
```

### 5. View in Browser

Open http://localhost:3002 in your browser to use the web interface!

## 🎯 Test Different Scenarios

### Approved Claims (Low Amount)
```bash
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL001" \
  -F "claimType=auto" \
  -F "description=Minor fender bender" \
  -F "amount=500" \
  -F "contactEmail=test@example.com"
```

### Rejected Claims (Over Coverage)
```bash
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL001" \
  -F "claimType=auto" \
  -F "description=Total loss" \
  -F "amount=100000" \
  -F "contactEmail=test@example.com"
```

### Invalid Policy
```bash
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=INVALID" \
  -F "claimType=auto" \
  -F "description=Test" \
  -F "amount=1000" \
  -F "contactEmail=test@example.com"
```

## 🔍 Monitor with Observability Stack

### View Traces in Jaeger
1. Go to http://localhost:16686
2. Select "insurance-claims-agent" service
3. Click "Find Traces"
4. Explore request flows and timing

### View Metrics in Prometheus
1. Go to http://localhost:9090
2. Try these queries:
   - `http_requests_total` - Total requests
   - `claims_submitted_total` - Claims by type
   - `http_request_duration_seconds` - Response times
   - `rate(http_requests_total[5m])` - Request rate

### AI Problem Detection
1. Go to http://localhost:8000
2. View real-time problem detection
3. See AI-generated recommendations

## 💾 Demo Data

The system comes with pre-configured policies:

- **POL001**: Auto insurance, $50,000 coverage
- **POL002**: Home insurance, $250,000 coverage  
- **POL003**: Health insurance, $100,000 coverage

## 🛑 Stop the System

```bash
# Stop the Flask app
pkill -f app_local

# Stop the observability stack
cd observability
docker-compose down
```

## 🔄 Restart Everything

```bash
# Start observability stack
cd observability
python start_observability.py

# Start app (in another terminal)
cd app
PORT=3002 python app_local.py
```

## 📊 What to Observe

### Metrics in Prometheus:
- Request counts by endpoint
- Response times (histograms)
- Claims submitted by type
- Active claims count

### Traces in Jaeger:
- Full request lifecycle
- Claim processing steps
- Timing breakdowns
- Error tracking

### AI Problem Detection:
- Automatic anomaly detection
- Error pattern recognition
- Performance degradation alerts
- Actionable recommendations

## 🎓 Learning Points

This setup demonstrates:
1. **Microservices observability** with OpenTelemetry
2. **Distributed tracing** across components
3. **Metrics collection** with Prometheus
4. **AI-powered monitoring** with custom agent
5. **Real-time problem detection**

All running locally without cloud dependencies!

## 🐛 Troubleshooting

### App won't start
- Check if port 3002 is free: `lsof -i :3002`
- Try a different port: `PORT=3003 python app_local.py`

### Can't submit claims
- Check app is running: `curl http://localhost:3002/health`
- Check logs in terminal where app is running

### Observability stack issues
- Check Docker: `docker ps`
- Restart stack: `cd observability && docker-compose restart`
- View logs: `docker-compose logs [service-name]`

## 🎉 Success!

You now have a complete observability platform running locally with:
✅ Metrics, Logs, and Traces
✅ AI-powered problem detection  
✅ Real-time monitoring dashboards
✅ Full insurance claims workflow

Happy monitoring! 🚀
