# 📊 Prometheus Query Guide

Your metrics are now flowing into Prometheus! Here are useful queries to explore your data.

## ✅ **Working Metrics**

Your Flask app is now being scraped by Prometheus every 5 seconds on port 3002.

## 🎯 **Essential Queries**

### **1. Claims by Status**
```promql
sum by (status) (claims_submitted_total)
```
**Result**: approved: 6, rejected: 2

### **2. Claims by Type**
```promql
sum by (claim_type) (claims_submitted_total)
```
**Result**: auto: 7, life: 1

### **3. Total Claims**
```promql
sum(claims_submitted_total)
```

### **4. Approval Rate (%)**
```promql
sum(claims_submitted_total{status="approved"}) / sum(claims_submitted_total) * 100
```

### **5. Rejection Rate (%)**
```promql
sum(claims_submitted_total{status="rejected"}) / sum(claims_submitted_total) * 100
```

## 📈 **Performance Metrics**

### **6. Request Rate (per second)**
```promql
rate(http_requests_total[1m])
```

### **7. Request Rate by Endpoint**
```promql
sum by (endpoint) (rate(http_requests_total[5m]))
```

### **8. Total Requests**
```promql
sum(http_requests_total)
```

### **9. Requests by Status Code**
```promql
sum by (status) (http_requests_total)
```

### **10. Error Rate**
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

## ⏱️ **Timing Metrics**

### **11. Average Response Time**
```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

### **12. 95th Percentile Response Time**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### **13. 99th Percentile Response Time**
```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### **14. Claims Processing Time (95th percentile)**
```promql
histogram_quantile(0.95, rate(claims_processing_seconds_bucket[5m]))
```

## 📊 **Business Metrics**

### **15. Auto Insurance Claims**
```promql
claims_submitted_total{claim_type="auto"}
```

### **16. High-Value Claims (if we tracked amounts)**
```promql
# This would require custom metrics
# Example: claims_amount_bucket{le="10000"}
```

### **17. Claims Growth Rate**
```promql
rate(claims_submitted_total[5m])
```

## 🎨 **Visualization Queries (for Grafana)**

### **18. Claims Over Time**
```promql
increase(claims_submitted_total[1m])
```

### **19. Request Throughput**
```promql
sum(rate(http_requests_total[30s]))
```

### **20. Active Claims Gauge**
```promql
active_claims_total
```

## 🔍 **Try in Prometheus UI**

1. **Open Prometheus**: http://localhost:9090
2. **Go to Graph tab**
3. **Paste any query above**
4. **Click "Execute"**
5. **Switch to "Graph" view** for visual representation

## 🌐 **Try via API**

### Query via cURL:
```bash
# Example: Claims by status
curl -s 'http://localhost:9090/api/v1/query?query=sum%20by%20(status)%20(claims_submitted_total)' | jq .

# Example: Total claims
curl -s 'http://localhost:9090/api/v1/query?query=sum(claims_submitted_total)' | jq -r '.data.result[0].value[1]'
```

### Query with time range:
```bash
# Last 5 minutes of data
curl -s 'http://localhost:9090/api/v1/query_range?query=claims_submitted_total&start='$(date -u -v-5M +%s)'&end='$(date -u +%s)'&step=30s' | jq .
```

## 📝 **Understanding PromQL**

### Selectors:
- `claims_submitted_total` - All claims
- `claims_submitted_total{status="approved"}` - Only approved
- `claims_submitted_total{status=~"approved|rejected"}` - Regex match

### Aggregations:
- `sum()` - Total across all labels
- `avg()` - Average value
- `max()` - Maximum value
- `min()` - Minimum value
- `count()` - Count of series

### Functions:
- `rate()` - Per-second rate
- `increase()` - Total increase
- `histogram_quantile()` - Calculate percentiles
- `by (label)` - Group by label

## 🎯 **Alert Rules (Example)**

Create these in Prometheus for production:

```yaml
# High error rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 2m
  annotations:
    summary: "High error rate detected"

# High claim rejection rate
- alert: HighRejectionRate
  expr: sum(claims_submitted_total{status="rejected"}) / sum(claims_submitted_total) > 0.5
  for: 5m
  annotations:
    summary: "More than 50% of claims are being rejected"

# Slow response time
- alert: SlowResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 5m
  annotations:
    summary: "95th percentile response time exceeds 1 second"
```

## 🧪 **Generate Data for Testing**

### Create traffic for metrics:
```bash
# Submit 20 claims
for i in {1..20}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=POL00$((1 + RANDOM % 3))" \
    -F "claimType=auto" \
    -F "description=Test $i" \
    -F "amount=$((RANDOM % 10000))" \
    -F "contactEmail=test@example.com" > /dev/null
  echo "Submitted claim $i"
done

# Then check metrics
curl -s 'http://localhost:9090/api/v1/query?query=sum(claims_submitted_total)' | jq -r '.data.result[0].value[1] + " total claims"'
```

## 🎓 **Learning Resources**

- **PromQL Basics**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Query Functions**: https://prometheus.io/docs/prometheus/latest/querying/functions/
- **Best Practices**: https://prometheus.io/docs/practices/naming/

## 💡 **Pro Tips**

1. **Use rate() for counters**: Counters always increase, use `rate()` to see per-second rate
2. **Use histogram_quantile() for percentiles**: Better than averages for understanding latency
3. **Group by relevant labels**: Use `by (label)` to aggregate meaningfully
4. **Start simple**: Begin with basic queries and add complexity
5. **Visualize in Grafana**: Prometheus is for queries, Grafana for dashboards

## 🎉 **Your Metrics are Live!**

You now have professional-grade metrics collection running. Every request, every claim, every error is being tracked!

**Current Stats:**
- ✅ 8 claims submitted
- ✅ 75% approval rate  
- ✅ Full request tracking
- ✅ Performance monitoring

Keep submitting claims and watch the metrics grow! 📊
