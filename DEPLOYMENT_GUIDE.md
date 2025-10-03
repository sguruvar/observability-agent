# Deployment Guide - Intelligent Observability Platform

This guide provides step-by-step instructions for deploying the complete observability platform.

## 🚀 Quick Deployment

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ installed
- Git installed
- At least 4GB RAM available
- Ports 3000, 3002, 4317, 4318, 5601, 8000, 9090, 9200, 9600, 16686 available

### 1. Clone and Setup
```bash
git clone https://github.com/sguruvar/observability-agent.git
cd observability-agent
```

### 2. Start Observability Stack
```bash
cd observability
docker-compose up -d
```

Wait for all services to be healthy (about 2-3 minutes):
```bash
docker-compose ps
```

### 3. Start Application
```bash
cd ../app
pip install -r requirements.txt
PORT=3002 python app_local.py
```

### 4. Verify Deployment
```bash
# Check all services
curl http://localhost:3002/health  # Application
curl http://localhost:8000/health  # AI Agent
curl http://localhost:9090/api/v1/targets  # Prometheus
curl http://localhost:9200/_cluster/health  # OpenSearch
curl http://localhost:16686/api/services  # Jaeger
```

## 🔧 Detailed Configuration

### Environment Variables
Create a `.env` file in the root directory:
```bash
# Application Configuration
PORT=3002
FLASK_ENV=development

# Observability Stack URLs
PROMETHEUS_URL=http://localhost:9090
OPENSEARCH_URL=http://localhost:9200
JAEGER_URL=http://localhost:16686
JAEGER_OTLP_ENDPOINT=http://localhost:4317

# AI Agent Configuration
AI_AGENT_PORT=8000
CORRELATION_UPDATE_INTERVAL=10
```

### Docker Compose Customization
Edit `observability/docker-compose.yml` to customize:
- Resource limits
- Volume mounts
- Network configuration
- Environment variables

### Prometheus Configuration
Edit `observability/prometheus.yml` to:
- Add new scrape targets
- Configure alerting rules
- Set retention policies
- Customize scrape intervals

## 📊 Monitoring Setup

### 1. Prometheus Targets
Access http://localhost:9090/targets to verify:
- `flask-app` target is UP
- `ai-agent` target is UP
- All metrics are being scraped

### 2. OpenSearch Index Patterns
1. Go to http://localhost:5601
2. Create index pattern: `app-logs-*`
3. Set time field: `@timestamp`
4. Explore logs in Discover

### 3. Jaeger Service Map
1. Go to http://localhost:16686
2. Select service: `insurance-claims-agent`
3. View traces and service map
4. Analyze request flows

### 4. Grafana Dashboards
1. Go to http://localhost:3000 (admin/admin)
2. Import dashboard from `observability/grafana/provisioning/dashboards/`
3. Configure data sources
4. Customize panels

## 🧪 Testing Deployment

### 1. Generate Test Data
```bash
python test_correlation.py
```

### 2. Verify Data Flow
```bash
# Check metrics
curl "http://localhost:9090/api/v1/query?query=claims_submitted_total"

# Check logs
curl -X POST "http://localhost:9200/app-logs-*/_search" \
  -H "Content-Type: application/json" \
  -d '{"query":{"match_all":{}},"size":5}'

# Check traces
curl "http://localhost:16686/api/traces?service=insurance-claims-agent&limit=5"

# Check correlation
curl "http://localhost:8000/api/correlation/story"
```

### 3. Load Testing
```bash
# Submit multiple claims
for i in {1..10}; do
  curl -X POST http://localhost:3002/submit_claim \
    -H "Content-Type: application/json" \
    -d "{\"policy_number\": \"POL$i\", \"amount\": $((1000 + i*100)), \"description\": \"Test claim $i\"}"
done
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using ports
lsof -i :3002
lsof -i :9090
lsof -i :9200

# Kill processes if needed
sudo kill -9 <PID>
```

#### 2. Docker Issues
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Restart services
docker-compose up -d
```

#### 3. Application Not Starting
```bash
# Check Python dependencies
pip install -r app/requirements.txt

# Check environment variables
echo $PORT
echo $PROMETHEUS_URL
```

#### 4. Metrics Not Appearing
```bash
# Check Prometheus configuration
curl http://localhost:9090/api/v1/targets

# Check application metrics endpoint
curl http://localhost:3002/metrics
```

#### 5. Logs Not Appearing
```bash
# Check OpenSearch health
curl http://localhost:9200/_cluster/health

# Check application logs
docker logs observability-ai-agent
```

### Log Locations
```bash
# Application logs
docker logs observability-ai-agent

# Prometheus logs
docker logs observability-prometheus

# OpenSearch logs
docker logs observability-opensearch

# Jaeger logs
docker logs observability-jaeger

# Grafana logs
docker logs observability-grafana
```

## 🚀 Production Deployment

### 1. Security Considerations
- Change default passwords
- Enable SSL/TLS
- Configure authentication
- Set up firewall rules
- Use secrets management

### 2. Scaling
- Use external databases
- Configure load balancers
- Set up monitoring
- Implement backup strategies
- Use container orchestration

### 3. Monitoring
- Set up alerting rules
- Configure notification channels
- Monitor resource usage
- Track performance metrics
- Implement health checks

## 📈 Performance Tuning

### 1. Prometheus
- Adjust scrape intervals
- Configure retention policies
- Optimize query performance
- Set up federation

### 2. OpenSearch
- Tune JVM settings
- Configure sharding
- Optimize indexing
- Set up clustering

### 3. Jaeger
- Configure sampling rates
- Tune storage backends
- Optimize query performance
- Set up clustering

## 🔄 Maintenance

### 1. Regular Tasks
- Monitor disk usage
- Check service health
- Update dependencies
- Backup configurations
- Review logs

### 2. Updates
```bash
# Update application
git pull origin main
docker-compose down
docker-compose up -d

# Update dependencies
pip install -r app/requirements.txt --upgrade
```

### 3. Backup
```bash
# Backup configurations
tar -czf observability-backup-$(date +%Y%m%d).tar.gz observability/

# Backup data volumes
docker run --rm -v observability_opensearch-data:/data -v $(pwd):/backup alpine tar czf /backup/opensearch-data-$(date +%Y%m%d).tar.gz -C /data .
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for errors
3. Create an issue on GitHub
4. Check the documentation

---

**Happy Observing! 🎉**
