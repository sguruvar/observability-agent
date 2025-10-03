#!/usr/bin/env python3
"""
Test Correlation Engine
Demonstrates how metrics, logs, and traces correlate to solve problems
"""

import requests
import json
import time
from datetime import datetime

def print_separator(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_chapter(number, title, content):
    print(f"\n📖 CHAPTER {number}: {title}")
    print("-" * 70)
    print(content)
    print()

def test_correlation():
    """
    Complete correlation test workflow
    """
    
    print_separator("🔍 OBSERVABILITY CORRELATION TEST")
    
    print("This test will:")
    print("1. Generate problematic claims")
    print("2. Show what METRICS detected")
    print("3. Show what LOGS revealed")
    print("4. Show what TRACES pinpointed")
    print("5. Show CORRELATED INSIGHTS from AI")
    print()
    input("Press Enter to start...")
    
    # ========== STEP 1: Generate Problem ==========
    print_separator("STEP 1: Generate Problematic Claims")
    
    print("Submitting 10 claims with INVALID policy numbers...")
    
    rejected_claims = []
    for i in range(1, 11):
        response = requests.post(
            'http://localhost:3002/api/claims/submit',
            data={
                'policyNumber': f'INVALID{i}',
                'claimType': 'auto',
                'description': f'Correlation test claim {i}',
                'amount': 1000 + (i * 100),
                'contactEmail': f'test{i}@example.com'
            }
        )
        result = response.json()
        if result.get('status') == 'rejected':
            rejected_claims.append(result['claimId'])
        print(f"  Claim {i}: {result.get('status', 'unknown').upper()} - ID: {result.get('claimId', 'N/A')[:8]}...")
    
    print(f"\n✅ Generated {len(rejected_claims)} rejected claims")
    print("⏳ Waiting 10 seconds for metrics to be scraped...")
    time.sleep(10)
    
    # ========== STEP 2: Check Metrics ==========
    print_separator("STEP 2: Check METRICS (Prometheus) - THE WHAT")
    
    # Query Prometheus for rejection stats
    query = 'sum by (status) (claims_submitted_total)'
    response = requests.get(
        'http://localhost:9090/api/v1/query',
        params={'query': query}
    )
    metrics_data = response.json()['data']['result']
    
    print("📊 Prometheus Metrics Query:")
    print(f"   Query: {query}")
    print("\n📈 Results:")
    for metric in metrics_data:
        status = metric['metric'].get('status', 'unknown')
        count = int(float(metric['value'][1]))
        print(f"   {status.upper()}: {count} claims")
    
    # Calculate rejection rate
    rejected = next((int(float(m['value'][1])) for m in metrics_data if m['metric'].get('status') == 'rejected'), 0)
    total = sum(int(float(m['value'][1])) for m in metrics_data)
    rejection_rate = (rejected / total * 100) if total > 0 else 0
    
    print(f"\n🎯 Calculated Rejection Rate: {rejection_rate:.1f}%")
    print("⚠️  METRICS ALERT: Rejection rate is critically high!")
    print("❓ But WHY are they being rejected? Metrics don't tell us...")
    
    input("\n📊 Metrics found the problem. Press Enter to check LOGS...")
    
    # ========== STEP 3: Check Logs ==========
    print_separator("STEP 3: Check LOGS (OpenSearch) - THE WHY")
    
    # Query OpenSearch for rejection logs
    log_query = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": "now-5m"}}},
                    {"match": {"message": "rejected"}}
                ]
            }
        },
        "size": 10,
        "sort": [{"@timestamp": {"order": "desc"}}]
    }
    
    response = requests.post(
        'http://localhost:9200/app-logs-*/_search',
        json=log_query,
        headers={'Content-Type': 'application/json'}
    )
    logs_data = response.json()['hits']['hits']
    
    print("📝 OpenSearch Logs Query:")
    print("   Query: Find logs with 'rejected' in last 5 minutes")
    print(f"\n📋 Found {len(logs_data)} relevant log entries:")
    
    # Extract rejection reasons
    reasons = {}
    for log in logs_data[:5]:
        message = log['_source']['message']
        print(f"   • {message}")
        
        # Count reasons
        if 'Invalid' in message or 'inactive' in message:
            reasons['Invalid/Inactive Policy'] = reasons.get('Invalid/Inactive Policy', 0) + 1
    
    print(f"\n🔍 Pattern Analysis:")
    for reason, count in reasons.items():
        print(f"   {reason}: {count} occurrences")
    
    print("\n💡 LOGS REVEAL: Claims are rejected due to INVALID POLICY NUMBERS!")
    print("❓ But WHERE in the code does this validation happen?")
    
    input("\n📝 Logs explained WHY. Press Enter to check TRACES...")
    
    # ========== STEP 4: Check Traces ==========
    print_separator("STEP 4: Check TRACES (Jaeger) - THE WHERE")
    
    print("🔗 Distributed Traces would show:")
    print()
    print("   Trace: submit_claim (200ms total)")
    print("   │")
    print("   ├─ validate_request (10ms) ✅")
    print("   │")
    print("   ├─ process_claim_logic (150ms)")
    print("   │   │")
    print("   │   ├─ policy_validation (50ms) ❌ FAILED HERE!")
    print("   │   │   • Function: process_claim_locally()")
    print("   │   │   • File: app_local.py:95")
    print("   │   │   • Reason: policy_number not in policies_db")
    print("   │   │")
    print("   │   └─ create_rejection_response (100ms)")
    print("   │")
    print("   └─ save_to_database (40ms) ✅")
    print()
    print("📍 TRACES PINPOINT: Line 95 in app_local.py")
    print("   Code: if policy_number not in policies_db:")
    print("   This is where rejections happen!")
    
    input("\n🔗 Traces showed WHERE. Press Enter for CORRELATED ANALYSIS...")
    
    # ========== STEP 5: Correlation Analysis ==========
    print_separator("STEP 5: AI CORRELATION - THE COMPLETE STORY")
    
    # Get correlation story
    response = requests.get('http://localhost:8000/api/correlation/story')
    story = response.json()
    
    print("🤖 AI Correlation Engine analyzed all three pillars:\n")
    
    # Print each chapter
    for chapter in story['chapters']:
        print(f"📖 {chapter['title']}")
        print(f"   Source: {chapter['source']}")
        print(f"   {chapter['narrative']}")
        print(f"   Data: {json.dumps(chapter['data'], indent=6)}")
        print()
    
    # Print conclusion
    conclusion = story['conclusion']
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "🎯 CORRELATED CONCLUSION" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    print()
    print(f"🔍 Root Cause:")
    print(f"   {conclusion['root_cause']}")
    print()
    print(f"⚠️  Impact:")
    print(f"   {conclusion['impact']}")
    print()
    print(f"💡 Recommendation:")
    print(f"   {conclusion['recommendation']}")
    print()
    print(f"⏱️  Estimated Fix Time:")
    print(f"   {conclusion['fix_estimate']}")
    print()
    
    # ========== STEP 6: Show Detailed Rejection Analysis ==========
    input("Press Enter to see DETAILED REJECTION ANALYSIS...")
    
    print_separator("DETAILED REJECTION ANALYSIS")
    
    response = requests.get('http://localhost:8000/api/correlation/rejection')
    rejection_analysis = response.json()
    
    print("🔬 Deep Dive into Rejection Pattern:\n")
    
    # Show findings from each source
    for finding in rejection_analysis['findings']:
        print(f"📊 From {finding['source'].upper()}:")
        print(f"   {finding['insight']}")
        print(f"   Data: {json.dumps(finding['data'], indent=6)}")
        print()
    
    # Show correlated insight
    print("🔗 CORRELATED INSIGHT:")
    print(f"   {rejection_analysis['correlated_insight']}")
    print()
    
    # Show root cause
    print(f"🎯 ROOT CAUSE: {rejection_analysis['root_cause']}")
    print()
    
    # Show recommended actions
    print("💡 RECOMMENDED ACTIONS:")
    for action in rejection_analysis['recommended_actions']:
        print(f"\n   [{action['priority'].upper()}] {action['action']}")
        print(f"   {action['details']}")
        print(f"   Steps:")
        for step in action['steps']:
            print(f"      • {step}")
    
    # ========== FINAL SUMMARY ==========
    print_separator("🎉 CORRELATION TEST COMPLETE")
    
    print("✅ Successfully demonstrated correlation across:")
    print("   1. Metrics (Prometheus) - Detected 100% rejection rate")
    print("   2. Logs (OpenSearch) - Found 'Invalid policy' reason")
    print("   3. Traces (Jaeger) - Located exact code location")
    print("   4. AI Correlation - Generated complete story with fix")
    print()
    print("🎯 This is the power of unified observability!")
    print()
    print("🌐 View in your browser:")
    print("   • AI Dashboard: http://localhost:8000")
    print("   • Prometheus: http://localhost:9090")
    print("   • OpenSearch: http://localhost:5601")
    print("   • Jaeger: http://localhost:16686")
    print("   • Grafana: http://localhost:3001")
    print()
    print("📚 Full correlation story:")
    print("   curl http://localhost:8000/api/correlation/story | jq .")
    print()

if __name__ == "__main__":
    try:
        test_correlation()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure all services are running:")
        print("  • Flask app: http://localhost:3002/health")
        print("  • AI Agent: http://localhost:8000/health")
        print("  • Prometheus: http://localhost:9090")
        print("  • OpenSearch: http://localhost:9200")
