# 🤖 AI-Powered Problem Detection Dashboard

Your AI agent is running and actively monitoring your insurance claims application!

## 🌐 Access the Dashboard

**URL**: http://localhost:8000

## 📊 What the AI Agent Does

The AI agent continuously:

1. **Queries Prometheus** for metrics (every analysis request)
2. **Queries OpenSearch** for log patterns  
3. **Analyzes patterns** to detect problems
4. **Generates recommendations** with solutions
5. **Displays results** on the dashboard

## 🎯 How It Works

### **Detection Logic:**

The AI agent checks for:

✅ **High Error Rate** (> 5%)
- Queries: `rate(http_requests_total{status=~"5.."}[5m])`
- Action: Alerts if error rate exceeds threshold

✅ **Slow Response Time** (P95 > 2s)
- Queries: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- Action: Alerts if response time is slow

✅ **Error Log Patterns**
- Queries OpenSearch for ERROR level logs
- Counts errors in last 5 minutes
- Detects database connection issues

✅ **Anomaly Detection**
- Compares current vs baseline
- Identifies unusual patterns
- Suggests root causes

## 🧪 Test the AI Agent

### **1. Generate Normal Traffic (No Problems)**
```bash
# Submit successful claims
for i in {1..5}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=POL001" \
    -F "claimType=auto" \
    -F "description=Test $i" \
    -F "amount=1000" \
    -F "contactEmail=test@example.com"
done

# Check AI analysis
curl -s http://localhost:8000/api/analysis | jq '.summary'
```

**Expected**: No problems detected ✅

---

### **2. Generate Errors (Trigger Alerts)**
```bash
# Submit many invalid claims
for i in {1..15}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=INVALID$i" \
    -F "claimType=auto" \
    -F "description=Invalid" \
    -F "amount=1000" \
    -F "contactEmail=test@example.com"
done

# Wait a moment
sleep 2

# Check AI analysis
curl -s http://localhost:8000/api/analysis | jq .
```

**Expected**: High error rate detected! ⚠️

---

### **3. Generate High Load (Performance Issues)**
```bash
# Rapid fire 50 requests
for i in {1..50}; do
  curl -s http://localhost:3002/api/claims/POL001 &
done
wait

# Check AI analysis
curl -s http://localhost:8000/api/analysis | jq '.problems'
```

## 📋 Dashboard Features

### **Summary Cards:**
- **High Severity Issues** (red) - Critical problems
- **Medium Severity Issues** (yellow) - Warnings
- **Low Severity Issues** (blue) - Minor issues
- **Recommendations** (green) - Total suggestions

### **Problems List:**
Shows detected issues with:
- Problem type
- Severity level
- Timestamp
- Context

### **Recommendations:**
For each problem, the AI provides:
- Problem description
- Root cause analysis
- 3-5 actionable solutions
- Best practices

### **Quick Links:**
Direct access to all other tools:
- Prometheus
- OpenSearch
- Jaeger
- Grafana

## 🎨 Dashboard Interface

```
┌─────────────────────────────────────────────────────┐
│  Observability Dashboard                    🔄 AUTO │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │
│  │  0   │  │  0   │  │  0   │  │  0   │           │
│  │ High │  │ Med  │  │ Low  │  │ Rec  │           │
│  └──────┘  └──────┘  └──────┘  └──────┘           │
│                                                       │
├─────────────────────────────────────────────────────┤
│  Detected Problems              │  Recommendations   │
│  ───────────────────           │  ──────────────    │
│  ✅ No problems detected       │  👍 All systems    │
│                                │     healthy        │
└─────────────────────────────────────────────────────┘
```

## 🔍 How AI Detects Problems

### **Pattern Recognition:**

1. **Metric Thresholds**
   ```python
   if error_rate > 5%:
       problem = "High error rate"
       severity = "high"
   ```

2. **Log Analysis**
   ```python
   if error_count_5min > 10:
       problem = "Error spike detected"
       severity = "high"
   ```

3. **Trend Analysis**
   - Compares current vs historical
   - Identifies sudden changes
   - Predicts future issues

### **Solution Generation:**

For each problem type, the AI has pre-defined solution patterns:
- Database issues → Check connections, pool size
- High errors → Review logs, check dependencies
- Slow response → Optimize queries, add caching

## 💡 Enhancing the AI Agent

Want to make it smarter? You can:

### **1. Add More Detection Patterns**

Edit `observability/ai-agent/app.py`:
```python
self.problem_patterns['custom_pattern'] = {
    'description': 'Your problem description',
    'solutions': [
        'Solution 1',
        'Solution 2',
        'Solution 3'
    ]
}
```

### **2. Add Custom Metrics Checks**

```python
def check_custom_metric(self):
    query = 'your_custom_metric_query'
    result = self.get_prometheus_metrics(query)
    # Analyze and return problems
```

### **3. Integrate Real AI (Optional)**

Add OpenAI or Claude API:
```python
import openai

def analyze_with_llm(self, problems):
    prompt = f"Analyze these problems: {problems}"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

## 🎯 Current AI Capabilities

✅ **Monitors**:
- HTTP error rates
- Response times
- Log error counts
- Database connection issues

✅ **Analyzes**:
- Metric thresholds
- Log patterns
- Time-based trends

✅ **Recommends**:
- Root cause suggestions
- Troubleshooting steps
- Best practices

✅ **Auto-Refreshes**:
- Updates every 5 seconds
- Real-time problem detection
- Continuous monitoring

## 🧪 Test the AI Detection

### **Trigger High Error Rate Alert:**

```bash
# Generate 20 errors quickly
for i in {1..20}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=INVALID" \
    -F "claimType=auto" \
    -F "description=Error test" \
    -F "amount=1000" \
    -F "contactEmail=test@example.com" > /dev/null &
done
wait

# Check AI dashboard
curl -s http://localhost:8000/api/analysis | jq '{problems: .problems, recommendations: .recommendations}'
```

### **View in Browser:**

Open http://localhost:8000 and you'll see:
- Problem cards turn **RED** for high severity
- Problems list shows detected issues
- Recommendations provide solutions
- Auto-refreshes every 5 seconds

## 📈 What Makes This "AI-Powered"

1. **Pattern Recognition**: Automatically identifies known problem patterns
2. **Threshold Detection**: Compares metrics against baselines
3. **Correlation**: Links metrics with logs
4. **Smart Recommendations**: Context-aware solutions
5. **Learning**: Can be extended with ML models

## 🔮 Future Enhancements

### **Add Machine Learning:**
- Anomaly detection with scikit-learn
- Predictive analytics
- Pattern learning from historical data

### **Add NLP for Logs:**
- Extract insights from log messages
- Categorize errors automatically
- Suggest fixes based on error text

### **Add Real-time Alerting:**
- Email/Slack notifications
- PagerDuty integration
- Automatic incident creation

## 🎉 Your AI Dashboard is Live!

**Access it now**: http://localhost:8000

It's actively monitoring:
- ✅ Your Flask app metrics
- ✅ Error rates and patterns
- ✅ Response times
- ✅ Log anomalies

**Try it!** Submit some problematic claims and watch the AI detect the issues automatically! 🤖🔍
