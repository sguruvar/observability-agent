# 🔍 Explore Your Observability Data

You've submitted claims! Now let's see how the observability stack captured everything.

## 📊 **1. View Metrics in Prometheus**

### Open Prometheus
Go to: **http://localhost:9090**

### Try These Queries:

1. **Total Claims Submitted**
   ```promql
   claims_submitted_total
   ```
   You should see 3 claims (1 approved, 2 rejected)

2. **Claims by Type**
   ```promql
   sum by (claim_type) (claims_submitted_total)
   ```

3. **Claims by Status**
   ```promql
   sum by (status) (claims_submitted_total)
   ```

4. **Request Rate (last 5 minutes)**
   ```promql
   rate(http_requests_total[5m])
   ```

5. **Response Time (95th percentile)**
   ```promql
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

6. **Claims Processing Time**
   ```promql
   histogram_quantile(0.95, rate(claims_processing_seconds_bucket[5m]))
   ```

## 🔗 **2. View Traces in Jaeger**

### Open Jaeger
Go to: **http://localhost:16686**

### What to Look For:

1. **Select Service**: `insurance-claims-agent`
2. **Click "Find Traces"**
3. **Explore Your Claims**:
   - You should see 3+ traces
   - Click on any trace to see the full request flow
   - Look for spans like:
     - `submit_claim` - Main claim submission
     - `process_claim_logic` - Business logic processing
     - `health_check` - Health checks

4. **Trace Details**:
   - **Duration**: How long each step took
   - **Tags**: Claim ID, policy number, amount
   - **Timeline**: Visual representation of the call stack

### Example Trace Structure:
```
submit_claim (200ms)
  ├─ process_claim_logic (150ms)
  │   ├─ Policy validation (50ms)
  │   └─ Decision logic (100ms)
  └─ Database store (50ms)
```

## 🤖 **3. AI Problem Detection Dashboard**

### Open AI Dashboard
Go to: **http://localhost:8000**

### What You'll See:

1. **Problem Summary Cards**:
   - High severity issues
   - Medium severity issues
   - Low severity issues
   - Total recommendations

2. **Detected Problems**:
   - Real-time analysis of your metrics and logs
   - Pattern recognition
   - Anomaly detection

3. **AI Recommendations**:
   - Actionable solutions for detected issues
   - Root cause analysis
   - Best practices

### Quick Links on Dashboard:
- Direct links to Prometheus, Jaeger, OpenSearch, Grafana

## 📈 **4. Grafana Dashboards**

### Open Grafana
Go to: **http://localhost:3001**
- Username: `admin`
- Password: `admin`

### Create Your First Dashboard:

1. Click **"+"** → **"Dashboard"**
2. Click **"Add new panel"**
3. Try these metrics:
   - `http_requests_total`
   - `claims_submitted_total`
   - `http_request_duration_seconds`

## 🔎 **5. OpenSearch Logs**

### Open OpenSearch Dashboards
Go to: **http://localhost:5601**

### Setup (First Time):
1. Wait for OpenSearch to fully start (may take 1-2 minutes)
2. Create an index pattern if prompted
3. Search for logs from your application

## 🧪 **Generate More Data**

Let's create some interesting patterns for the AI to detect:

### Simulate High Load:
```bash
# Submit 10 claims rapidly
for i in {1..10}; do
  curl -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=POL001" \
    -F "claimType=auto" \
    -F "description=Claim $i" \
    -F "amount=$((RANDOM % 10000))" \
    -F "contactEmail=test$i@example.com"
done
```

### Create Error Patterns:
```bash
# Submit invalid claims
for i in {1..5}; do
  curl -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=INVALID$i" \
    -F "claimType=auto" \
    -F "description=Invalid claim $i" \
    -F "amount=1000" \
    -F "contactEmail=test@example.com"
done
```

### Test Different Amounts:
```bash
# Small claim (auto-approved)
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL001" -F "claimType=auto" \
  -F "description=Minor scratch" -F "amount=500" \
  -F "contactEmail=test@example.com"

# Large claim (rejected)
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL001" -F "claimType=auto" \
  -F "description=Total loss" -F "amount=75000" \
  -F "contactEmail=test@example.com"

# Medium claim (might need review)
curl -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL002" -F "claimType=home" \
  -F "description=Roof damage" -F "amount=15000" \
  -F "contactEmail=test@example.com"
```

## 📊 **What the Observability Stack Captures**

### For Each Claim Submission:

**Metrics** (Prometheus):
- ✅ Request count by endpoint
- ✅ Response time histogram
- ✅ Claims submitted by type
- ✅ Claims by status (approved/rejected)
- ✅ Processing time

**Traces** (Jaeger):
- ✅ Full request lifecycle
- ✅ Each processing step with timing
- ✅ Claim metadata (ID, amount, policy)
- ✅ Error tracking if any

**Logs** (OpenSearch):
- ✅ Application logs
- ✅ Claim processing events
- ✅ Decision reasoning
- ✅ Error details

**AI Analysis**:
- ✅ Pattern detection
- ✅ Anomaly identification
- ✅ Performance monitoring
- ✅ Error rate analysis

## 🎯 **Key Observability Patterns to Look For**

### 1. **Performance Degradation**
After submitting many claims, check if:
- Response times are increasing
- Processing times are slower

### 2. **Error Patterns**
Submit invalid claims and see:
- Error rate metrics spike
- Error traces in Jaeger
- AI agent detecting the pattern

### 3. **Business Metrics**
Monitor:
- Approval vs rejection ratio
- Average claim amount
- Claims by type distribution

### 4. **System Health**
Watch for:
- Memory usage trends
- Request rate patterns
- Active connections

## 🔮 **Advanced: Correlate Across Tools**

### Example Investigation Flow:

1. **AI Dashboard alerts** about high error rate
2. **Prometheus** confirms error spike in metrics
3. **Jaeger** shows which requests are failing
4. **OpenSearch** provides detailed error logs
5. **You** identify root cause and fix!

This is the power of unified observability! 🚀

## 💡 **Tips for Exploration**

1. **Keep submitting claims** while exploring - see real-time updates
2. **Try different claim amounts** to trigger different decisions
3. **Use invalid policy numbers** to create errors
4. **Monitor the AI dashboard** for automatic problem detection
5. **Create custom Prometheus queries** for your specific needs

## 🎓 **What You're Learning**

This setup demonstrates professional-grade observability:
- ✅ Distributed tracing across services
- ✅ Metrics collection and aggregation
- ✅ Log centralization and search
- ✅ AI-powered problem detection
- ✅ Real-time monitoring and alerting

All the techniques used here scale to production systems with hundreds of microservices!

## 🎉 **You're Now a Observability Pro!**

You have a complete Lightrun-style observability platform that:
- Captures every request
- Traces execution flow
- Collects business metrics
- Detects problems automatically
- Provides actionable insights

Keep exploring and see what patterns you can find! 🔍
