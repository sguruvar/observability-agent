# 📊 Grafana Dashboard Guide

Beautiful visualizations for your insurance claims metrics!

## 🌐 Access Grafana

**URL**: http://localhost:3001

**Credentials**:
- Username: `admin`
- Password: `admin`
- (You may be asked to change password - you can skip it)

## ✅ What's Pre-Configured

Your Grafana instance comes with:

1. **✅ Prometheus Data Source** - Already connected
2. **✅ Insurance Claims Dashboard** - Pre-built dashboard
3. **✅ Auto-refresh** - Updates every 5 seconds

## 🎯 View the Pre-Built Dashboard

### **Step 1: Login**
1. Go to http://localhost:3001
2. Login with `admin` / `admin`
3. Skip password change (or set a new one)

### **Step 2: Open Dashboard**
1. Click the **☰ menu** (top left)
2. Go to **"Dashboards"**
3. Click **"Insurance Claims Overview"**

### **Step 3: Explore!**
You'll see:
- Total claims submitted
- Claims by status (pie chart)
- Approval rate (gauge)
- Rejection rate (gauge)
- Claims over time (line chart)
- Claims by type (bar chart)
- HTTP request rate
- Processing time (P95)

## 📊 Dashboard Panels

### **Panel 1: Total Claims**
- **Type**: Big Number
- **Metric**: `sum(claims_submitted_total)`
- **Current Value**: 15 claims
- **Color**: Changes based on volume

### **Panel 2: Claims by Status**
- **Type**: Pie Chart
- **Metric**: `sum by (status) (claims_submitted_total)`
- **Shows**: Distribution of approved/rejected/pending
- **Current**: 100% rejected (shows the problem!)

### **Panel 3: Approval Rate**
- **Type**: Gauge
- **Formula**: `sum(approved) / sum(total) * 100`
- **Current**: 0% (all rejected)
- **Threshold**: Red < 50%, Yellow 50-80%, Green > 80%

### **Panel 4: Rejection Rate**
- **Type**: Gauge  
- **Formula**: `sum(rejected) / sum(total) * 100`
- **Current**: 100% (🚨 RED ALERT!)
- **Threshold**: Green < 20%, Yellow 20-50%, Red > 50%

### **Panel 5: Claims Over Time**
- **Type**: Time Series
- **Shows**: Trend of claims by status
- **Auto-refresh**: Updates every 5 seconds
- **Useful for**: Spotting trends and spikes

### **Panel 6: Claims by Type**
- **Type**: Bar Chart
- **Shows**: Distribution across auto, home, health, life
- **Current**: Only auto claims

### **Panel 7: HTTP Request Rate**
- **Type**: Graph
- **Metric**: `rate(http_requests_total[1m])`
- **Shows**: Requests per second by endpoint
- **Useful for**: Traffic monitoring

### **Panel 8: Processing Time**
- **Type**: Graph
- **Metric**: P95 processing time
- **Shows**: 95th percentile claim processing duration
- **Useful for**: Performance monitoring

## 🎨 Create Your Own Dashboard

### **1. Create New Dashboard**
1. Click **"+"** in the left sidebar
2. Select **"Dashboard"**
3. Click **"Add new panel"**

### **2. Add a Panel**

**Example: Claims Approval vs Rejection**
```promql
Query: sum by (status) (claims_submitted_total)
Visualization: Time series
Legend: {{status}}
```

**Example: Request Count**
```promql
Query: sum(http_requests_total)
Visualization: Stat
Title: Total Requests
```

**Example: Average Response Time**
```promql
Query: rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
Visualization: Graph
Unit: seconds
```

## 🔧 Useful Panel Queries

### **Business Metrics:**

**1. Claim Success Rate (Last Hour)**
```promql
sum(increase(claims_submitted_total{status="approved"}[1h])) / 
sum(increase(claims_submitted_total[1h])) * 100
```

**2. Claims Value by Status**
```promql
sum by (status) (claims_submitted_total)
```

**3. Active Claims**
```promql
active_claims_total
```

### **Performance Metrics:**

**4. Request Rate (Per Minute)**
```promql
sum(rate(http_requests_total[1m])) * 60
```

**5. Error Rate**
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / 
sum(rate(http_requests_total[5m])) * 100
```

**6. P99 Response Time**
```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### **Health Metrics:**

**7. Uptime**
```promql
up{job="flask-app"}
```

**8. Scrape Duration**
```promql
scrape_duration_seconds{job="flask-app"}
```

## 🎯 Dashboard Features

### **Time Range Picker**
- Top right corner
- Quick ranges: Last 5m, 15m, 1h, 6h, 24h
- Custom range selector

### **Refresh Controls**
- Auto-refresh dropdown (top right)
- Set to 5s, 10s, 30s, 1m, etc.
- Manual refresh button

### **Variables**
Add dashboard variables for filtering:
- `$status` - Filter by claim status
- `$claim_type` - Filter by claim type
- `$time_range` - Dynamic time ranges

### **Annotations**
Mark important events:
- Deployments
- Incidents
- Configuration changes

## 📈 Advanced Features

### **Alerting**
Set up alerts directly in Grafana:

1. **Edit a panel**
2. Go to **Alert** tab
3. **Create Alert Rule**:
   - Condition: `WHEN avg() OF query(A, 5m) IS ABOVE 50`
   - For: High rejection rate
   - Actions: Email, Slack, webhook

### **Dashboard Templates**
Variables for dynamic dashboards:

```
Name: status
Type: Query
Query: label_values(claims_submitted_total, status)
```

Then use in query:
```promql
claims_submitted_total{status="$status"}
```

## 🎨 Visualization Types

### **Available in Grafana:**

- **Time Series** - Line/area charts over time
- **Stat** - Single big number
- **Gauge** - Semi-circle gauge with thresholds
- **Bar Chart** - Horizontal/vertical bars
- **Pie Chart** - Circular percentage view
- **Table** - Tabular data
- **Heatmap** - Density visualization
- **Graph (old)** - Classic line graph

## 🧪 Test Your Dashboard

### **Generate Diverse Data:**

```bash
# Submit successful claims
for i in {1..10}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=POL00$((1 + RANDOM % 3))" \
    -F "claimType=auto" \
    -F "description=Success test $i" \
    -F "amount=$((500 + RANDOM % 5000))" \
    -F "contactEmail=test$i@example.com" > /dev/null
  sleep 0.2
done

# Watch the dashboard update in real-time!
```

Then watch:
- **Approval rate gauge** go up (green!)
- **Rejection rate gauge** go down
- **Pie chart** rebalance
- **Time series** show the trend

## 💡 Pro Tips

### **1. Dashboard Best Practices**
- Group related panels together
- Use consistent colors (red=bad, green=good)
- Show both absolute numbers and rates
- Include time-based trends

### **2. Query Optimization**
- Use recording rules for complex queries
- Set appropriate time ranges
- Limit series cardinality

### **3. Alerting Strategy**
- Alert on symptoms, not causes
- Set appropriate thresholds
- Include context in alert messages
- Avoid alert fatigue

## 🔗 Integration with Other Tools

### **From Grafana, Jump To:**

**Logs**: Click a metric spike → Note the time → Go to OpenSearch with that timeframe

**Traces**: Click an error → Note the timestamp → Search Jaeger for traces at that time

**AI Analysis**: Use Grafana for visualization, AI dashboard for recommendations

## 📚 Sample Dashboards to Create

### **1. Executive Dashboard**
- Total claims today
- Approval rate
- Average claim value
- Processing time trends

### **2. Operations Dashboard**
- Request rate
- Error rate
- Response time (P50, P95, P99)
- Active connections

### **3. Business Intelligence**
- Claims by type over time
- Approval rates by claim type
- Peak submission times
- Geographic distribution (if you add location data)

## 🎉 Your Grafana is Ready!

**Access Now**: http://localhost:3001 (admin/admin)

You should see:
- ✅ Prometheus data source connected
- ✅ "Insurance Claims Overview" dashboard
- ✅ Real-time data visualization
- ✅ **100% rejection rate** clearly visible (RED gauge!)

The dashboard will update every 5 seconds with live data!

## 🚀 Quick Actions

### **View Current Dashboard**
```
http://localhost:3001/d/insurance-claims
```

### **Explore Metrics**
```
http://localhost:3001/explore
```

### **Create Alert**
1. Edit any panel
2. Alert tab
3. Create alert rule
4. Add notification channel

## 🎓 Learning Resources

- **Grafana Docs**: https://grafana.com/docs/grafana/latest/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Dashboard Gallery**: https://grafana.com/grafana/dashboards/

Now open http://localhost:3001 and enjoy your beautiful dashboards! 📊✨
