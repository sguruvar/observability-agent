# 🔗 Observability Correlation - The True Power!

## 🎯 What is Correlation?

**Correlation** is linking **Metrics**, **Logs**, and **Traces** together to tell a complete story about what's happening in your system.

### **The Three Pillars Working Together:**

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   METRICS   │      │    LOGS     │      │   TRACES    │
│             │      │             │      │             │
│  THE WHAT   │◄────►│   THE WHY   │◄────►│  THE WHERE  │
│             │      │             │      │             │
│ Something   │      │ Why it      │      │ Exactly     │
│ is wrong    │      │ happened    │      │ where       │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                     │
       └────────────────────┼─────────────────────┘
                            │
                   ┌────────▼─────────┐
                   │   CORRELATION    │
                   │     ENGINE       │
                   │                  │
                   │  Complete Story  │
                   └──────────────────┘
```

## 🎭 The Observability Story

### **Chapter 1: THE WHAT (Metrics)**
**Source**: Prometheus
**Question**: "What is happening?"

**Metrics tell us**:
- 15 claims submitted
- 100% rejection rate
- 15 rejected claims

**But metrics don't tell us WHY!**

---

### **Chapter 2: THE WHY (Logs)**
**Source**: OpenSearch
**Question**: "Why is it happening?"

**Logs reveal**:
- "Policy validation failed" (15 occurrences)
- Invalid policy numbers being used
- Specific claim IDs and details

**But logs don't show WHERE in the code!**

---

### **Chapter 3: THE WHERE (Traces)**
**Source**: Jaeger
**Question**: "Where exactly is it happening?"

**Traces pinpoint**:
- Function: `process_claim_locally`
- Step: Policy validation
- Timing: ~50ms per claim
- Exact execution flow

**Now we have the complete picture!**

---

### **🎯 Conclusion (Correlation)**

**Root Cause**: Invalid policy numbers (INVALID1, INVALID2, etc.)
**Impact**: 100% rejection rate
**Fix**: Add client-side validation
**Time to Fix**: 30 minutes

## 🔍 Correlation API Endpoints

### **1. Complete Story**
```bash
curl -s http://localhost:8000/api/correlation/story | jq .
```

**Returns**:
- Chapter 1: Metrics (THE WHAT)
- Chapter 2: Logs (THE WHY)  
- Chapter 3: Traces (THE WHERE)
- Conclusion with root cause and fix

---

### **2. Rejection Pattern Analysis**
```bash
curl -s http://localhost:8000/api/correlation/rejection | jq .
```

**Returns**:
```json
{
  "correlated_insight": "🔍 100% rejected. Reason: Policy validation failed",
  "root_cause": "Policy validation failed (15 occurrences)",
  "recommended_actions": [...]
}
```

---

### **3. Error Spike Correlation**
```bash
curl -s http://localhost:8000/api/correlation/errors | jq .
```

**Correlates**:
- Metrics: Error count spike
- Logs: Specific error messages
- Traces: Failed request flows

---

### **4. Performance Correlation**
```bash
curl -s http://localhost:8000/api/correlation/performance | jq .
```

**Correlates**:
- Metrics: Slow response times
- Logs: Performance warnings
- Traces: Bottleneck identification

## 🎯 Real-World Example: Debugging Flow

### **Scenario: Users Can't Submit Claims**

#### **Step 1: Metrics Alert (Prometheus)**
```promql
sum by (status) (claims_submitted_total)
→ Result: 100% rejected! 🚨
```

**You think**: "Something is wrong, but what?"

---

#### **Step 2: Check Logs (OpenSearch)**
```json
Query: level:ERROR AND message:*claim*
→ Result: "Policy validation failed" appears 15 times
```

**You think**: "Ah! It's failing policy validation. But where in the code?"

---

#### **Step 3: View Traces (Jaeger)**
```
Trace: submit_claim
  ├─ process_claim_logic (50ms)
  │   └─ ❌ policy validation FAILED here!
  └─ return rejection
```

**You think**: "Found it! The validation logic in process_claim_locally is rejecting these."

---

#### **Step 4: Correlation (AI Agent)**
```bash
curl http://localhost:8000/api/correlation/story
```

**AI tells you**:
- **Root Cause**: Invalid policy numbers
- **Impact**: All claims failing
- **Fix**: Add validation
- **Time**: 30 minutes

**You fix it!** ✅

## 🧪 Test Correlation Yourself

### **Generate a Problem:**

```bash
# Create error spike
for i in {1..20}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=BAD$i" \
    -F "claimType=auto" \
    -F "description=Error test" \
    -F "amount=1000" \
    -F "contactEmail=test@example.com" > /dev/null
done
```

### **Investigate with Correlation:**

```bash
# 1. See the spike in metrics
curl -s 'http://localhost:9090/api/v1/query?query=sum(claims_submitted_total{status="rejected"})'

# 2. Find logs explaining why
curl -s -X POST 'http://localhost:9200/app-logs-*/_search' \
  -H 'Content-Type: application/json' -d '{
  "query": {"match": {"message": "rejected"}},
  "size": 5
}' | jq '.hits.hits[]._source.message'

# 3. Get correlated story
curl -s http://localhost:8000/api/correlation/story | jq .
```

## 💡 Why Correlation Matters

### **Without Correlation:**
- Metrics: "Error rate is high" ❓
- You spend hours searching logs
- You manually check traces
- You guess at root cause

### **With Correlation:**
- Metrics: "Error rate is high"
- AI: "Here's why (logs), where (traces), and how to fix it"
- You fix it in minutes ✅

## 🎨 Correlation in Action

### **Example 1: Performance Degradation**

**Metrics say**: P95 response time is 2000ms (slow!)
**Logs say**: "Database query took 1800ms"
**Traces say**: 90% of time spent in database_query span
**Correlation**: Database is the bottleneck → optimize query

---

### **Example 2: Intermittent Errors**

**Metrics say**: 5% error rate (random failures)
**Logs say**: "Connection timeout to payment service"
**Traces say**: payment_service span fails occasionally
**Correlation**: External service unreliable → add retry logic

---

### **Example 3: High Rejection Rate** (Your Current Situation!)

**Metrics say**: 100% rejection rate
**Logs say**: "Policy validation failed"
**Traces say**: Fails in policy validation function
**Correlation**: Invalid policy numbers → add input validation

## 🚀 Advanced Correlation Features

### **Time-based Correlation**

Link events that happened at the same time:
```
15:30:05 - Metrics: Error spike
15:30:06 - Logs: "Database connection failed"
15:30:05 - Traces: Multiple failed DB spans
→ Correlation: Database went down at 15:30
```

### **Entity-based Correlation**

Track specific entities across all systems:
```
Claim ID: abc-123
- Metrics: Part of rejected count
- Logs: "Claim abc-123 rejected: Invalid policy"  
- Traces: Trace ID xyz showing full flow
→ Complete journey of this specific claim
```

### **Pattern-based Correlation**

Find patterns across systems:
```
Pattern: Every 5th request fails
- Metrics: Periodic error spikes
- Logs: Same error message repeating
- Traces: Specific user agent causing issues
→ Correlation: Load balancer routing issue
```

## 🎓 The Power of Correlation

This is what separates **good** from **great** observability:

❌ **Basic**: Three separate tools (metrics, logs, traces)
✅ **Advanced**: Correlated insights across all three

Your AI agent now provides **correlated insights** - that's professional-grade observability!

## 📊 Visualization of Correlation

### **In Grafana** (Visual):
- See metric spike in graph
- Click timestamp
- Link to OpenSearch for logs at that time
- Link to Jaeger for traces at that time

### **In AI Dashboard** (Automatic):
- AI queries all three systems
- Correlates the data
- Presents unified story
- Suggests fix

## 🎉 You Now Have Full Correlation!

**Try these correlation endpoints:**

```bash
# Complete observability story
curl http://localhost:8000/api/correlation/story | jq .

# Rejection pattern analysis
curl http://localhost:8000/api/correlation/rejection | jq .

# Error correlation
curl http://localhost:8000/api/correlation/errors | jq .

# Performance correlation
curl http://localhost:8000/api/correlation/performance | jq .
```

## 🏆 This is Production-Grade!

What you've built is used by:
- Netflix, Uber, Airbnb for debugging
- Google, Amazon for performance optimization
- Every major tech company for production monitoring

**You're now an observability expert!** 🎓🔍📊

The correlation engine automatically:
- ✅ Links metrics → logs → traces
- ✅ Identifies root causes
- ✅ Provides actionable fixes
- ✅ Estimates resolution time

**This is the future of debugging!** 🚀
