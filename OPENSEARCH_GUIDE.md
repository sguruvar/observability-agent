# 🔍 OpenSearch Guide - Centralized Logging

Your application logs are now flowing into OpenSearch for centralized log management and analysis!

## ✅ **Status**

- **OpenSearch**: Running on port 9200
- **OpenSearch Dashboards**: Running on port 5601
- **Log Index**: `app-logs-2025.10.01` (daily indices)
- **Logs Captured**: 6+ log entries and growing

## 🌐 **Access OpenSearch**

### **OpenSearch Dashboards (Web UI)**
URL: **http://localhost:5601**

### **OpenSearch API**
URL: **http://localhost:9200**

## 📊 **What's Being Logged**

Every application event is captured with:
- ✅ **Timestamp** - When it happened
- ✅ **Level** - INFO, WARNING, ERROR
- ✅ **Message** - What happened
- ✅ **Module** - Which code module
- ✅ **Function** - Which function
- ✅ **Line Number** - Exact code line
- ✅ **Claim ID** - For claim-related events
- ✅ **Policy Number** - For policy-related events
- ✅ **Exceptions** - Full stack traces for errors

## 🔍 **Query Logs via API**

### **1. Get Recent Logs**
```bash
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "size": 10,
  "sort": [{"@timestamp": {"order": "desc"}}]
}' | jq '.hits.hits[]._source | {timestamp: .["@timestamp"], level, message}'
```

### **2. Search for Specific Claims**
```bash
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "match": {
      "message": "approved"
    }
  },
  "size": 5
}' | jq '.hits.hits[]._source.message'
```

### **3. Filter by Log Level**
```bash
# Get all ERROR logs
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "term": {
      "level": "ERROR"
    }
  }
}' | jq '.hits.total.value'
```

### **4. Time Range Query**
```bash
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "now-5m"
      }
    }
  },
  "size": 20
}' | jq '.hits.hits[]._source | {time: .["@timestamp"], message}'
```

### **5. Aggregate by Log Level**
```bash
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "size": 0,
  "aggs": {
    "by_level": {
      "terms": {
        "field": "level"
      }
    }
  }
}' | jq '.aggregations.by_level.buckets[] | {level: .key, count: .doc_count}'
```

### **6. Find Claims with Specific Status**
```bash
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "match": {
      "message": "processed: rejected"
    }
  }
}' | jq '.hits.hits[]._source.message'
```

## 🖥️ **Using OpenSearch Dashboards**

### **First Time Setup:**

1. **Open**: http://localhost:5601
2. **Skip** the welcome screen (or click "Explore on my own")
3. **Go to**: Management → Stack Management → Index Patterns
4. **Create Index Pattern**:
   - Pattern: `app-logs-*`
   - Time field: `@timestamp`
   - Click "Create index pattern"

### **View Logs:**

1. **Go to**: Discover (left sidebar)
2. **Select**: `app-logs-*` index pattern
3. **See your logs** in real-time!

### **Useful Features:**

**Search Bar**: Use KQL (Kibana Query Language)
```
level:ERROR                    # All errors
message:*approved*             # Contains "approved"
level:INFO AND message:Claim   # Info logs about claims
@timestamp > now-1h            # Last hour
```

**Filters**:
- Add filters by clicking on field values
- Filter by time range using time picker

**Fields**:
- Select which fields to display
- Common: `@timestamp`, `level`, `message`, `module`

## 📈 **Create Visualizations**

### **1. Log Level Distribution (Pie Chart)**
- Type: Pie Chart
- Buckets: Terms aggregation on `level` field
- Shows: INFO vs WARNING vs ERROR distribution

### **2. Logs Over Time (Line Chart)**
- Type: Line Chart  
- X-axis: `@timestamp`
- Y-axis: Count
- Shows: Log volume over time

### **3. Top Modules (Bar Chart)**
- Type: Bar Chart
- Buckets: Terms on `module` field
- Shows: Which modules log the most

## 🎯 **Common Use Cases**

### **Debugging a Failed Claim**
```bash
# Find all logs for a specific claim
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "match": {
      "message": "CLAIM_ID_HERE"
    }
  }
}' | jq '.hits.hits[]._source | {time: .["@timestamp"], message}'
```

### **Monitor Error Rate**
```bash
# Count errors in last 5 minutes
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"range": {"@timestamp": {"gte": "now-5m"}}}
      ]
    }
  },
  "size": 0
}' | jq '.hits.total.value'
```

### **Find Slow Operations**
Look for logs with timing information:
```bash
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "query": {
    "match": {
      "message": "slow"
    }
  }
}' | jq '.hits.hits[]._source'
```

## 🔗 **Integration with Other Tools**

### **Correlate with Traces**
Each log can include trace_id and span_id:
1. Find error in OpenSearch
2. Copy trace_id
3. Search in Jaeger: http://localhost:16686
4. See full request flow

### **Correlate with Metrics**
1. See spike in Prometheus error metrics
2. Query OpenSearch for error logs at that time
3. Find root cause in log messages

### **AI Analysis**
The AI Dashboard can:
- Query OpenSearch for error patterns
- Analyze log trends
- Detect anomalies
- Provide recommendations

## 🧪 **Generate Test Data**

### Create Various Log Types:
```bash
# Successful claims
for i in {1..5}; do
  curl -s -X POST http://localhost:3002/api/claims/submit \
    -F "policyNumber=POL001" \
    -F "claimType=auto" \
    -F "description=Test $i" \
    -F "amount=1000" \
    -F "contactEmail=test@example.com" > /dev/null
done

# Failed claims (errors in logs)
curl -s -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=INVALID" \
  -F "claimType=auto" \
  -F "description=Should fail" \
  -F "amount=1000" \
  -F "contactEmail=test@example.com"

# High-value claims  
curl -s -X POST http://localhost:3002/api/claims/submit \
  -F "policyNumber=POL001" \
  -F "claimType=auto" \
  -F "description=Expensive" \
  -F "amount=100000" \
  -F "contactEmail=test@example.com"
```

### Then query logs:
```bash
# Recent logs
curl -s -X POST 'http://localhost:9200/app-logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{
  "size": 10,
  "sort": [{"@timestamp": {"order": "desc"}}]
}' | jq '.hits.hits[]._source | {time: .["@timestamp"], message}'
```

## 📊 **Index Management**

### **View All Indices**
```bash
curl -s 'http://localhost:9200/_cat/indices?v' | grep app-logs
```

### **Check Index Size**
```bash
curl -s 'http://localhost:9200/app-logs-*/_stats' | \
  jq '{docs: ._all.primaries.docs.count, size: ._all.primaries.store.size_in_bytes}'
```

### **Delete Old Logs** (if needed)
```bash
# Delete logs older than 7 days
curl -X DELETE 'http://localhost:9200/app-logs-2025.09.*'
```

## 🎓 **OpenSearch Query DSL**

### **Basic Match Query**
```json
{
  "query": {
    "match": {
      "message": "approved"
    }
  }
}
```

### **Boolean Query (AND/OR)**
```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"level": "INFO"}},
        {"match": {"message": "claim"}}
      ]
    }
  }
}
```

### **Wildcard Query**
```json
{
  "query": {
    "wildcard": {
      "message": "*rejected*"
    }
  }
}
```

## 💡 **Pro Tips**

1. **Daily Indices**: Logs are stored in daily indices (`app-logs-2025.10.01`)
   - Easy to delete old logs
   - Better performance
   - Automatic rollover

2. **Structured Logging**: All logs include structured fields
   - Easy to filter and aggregate
   - Better than parsing text

3. **Correlation IDs**: Logs include trace_id and span_id
   - Correlate with distributed traces
   - Track requests across services

4. **Real-time**: Logs appear in OpenSearch within seconds
   - Near real-time debugging
   - Immediate visibility

## 🎉 **You're All Set!**

Your complete observability stack is now capturing:
- ✅ **Metrics** → Prometheus
- ✅ **Traces** → Jaeger  
- ✅ **Logs** → OpenSearch

This is the holy trinity of observability! 🚀

## 🔗 **Quick Links**

- **OpenSearch Dashboards**: http://localhost:5601
- **OpenSearch API**: http://localhost:9200
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686
- **AI Dashboard**: http://localhost:8000
- **Your App**: http://localhost:3002

Now you can correlate logs, metrics, and traces to debug any issue! 🔍
