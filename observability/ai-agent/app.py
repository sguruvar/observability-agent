#!/usr/bin/env python3
"""
AI Problem Detection Agent
Analyzes metrics, logs, and traces to identify issues
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template
import logging
from typing import Dict, List, Any
import threading
from correlation_engine import CorrelationEngine, analyze_complete_picture

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ObservabilityAnalyzer:
    def __init__(self):
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')
        self.opensearch_url = os.getenv('OPENSEARCH_URL', 'http://opensearch:9200')
        self.jaeger_url = os.getenv('JAEGER_URL', 'http://jaeger:14268')
        
        # Problem detection thresholds
        self.thresholds = {
            'error_rate': 0.05,  # 5% error rate
            'response_time_p95': 2000,  # 2 seconds
            'memory_usage': 0.8,  # 80% memory usage
            'cpu_usage': 0.8,  # 80% CPU usage
        }
        
        # Known problems and solutions
        self.problem_patterns = {
            'high_error_rate': {
                'description': 'High error rate detected',
                'solutions': [
                    'Check application logs for error patterns',
                    'Verify external service dependencies',
                    'Review recent code deployments'
                ]
            },
            'slow_response_time': {
                'description': 'Response time is above threshold',
                'solutions': [
                    'Check database query performance',
                    'Review external API response times',
                    'Consider adding caching'
                ]
            },
            'high_memory_usage': {
                'description': 'Memory usage is high',
                'solutions': [
                    'Check for memory leaks',
                    'Review garbage collection settings',
                    'Consider scaling horizontally'
                ]
            },
            'database_connection_issues': {
                'description': 'Database connection problems',
                'solutions': [
                    'Check database server status',
                    'Review connection pool settings',
                    'Verify network connectivity'
                ]
            },
            'high_claim_rejection_rate': {
                'description': 'Unusually high claim rejection rate detected',
                'solutions': [
                    'Review recent policy changes or updates',
                    'Check if policy validation logic is too strict',
                    'Verify policy numbers in submission requests',
                    'Investigate if fraud detection is too aggressive',
                    'Review claim amount limits and coverage amounts'
                ]
            }
        }

    def get_prometheus_metrics(self, query: str, duration: str = '5m') -> List[Dict]:
        """Query Prometheus for metrics"""
        try:
            url = f"{self.prometheus_url}/api/v1/query"
            params = {
                'query': query,
                'time': datetime.now().timestamp()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', {}).get('result', [])
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return []

    def get_opensearch_logs(self, query: Dict = None, size: int = 100) -> List[Dict]:
        """Query OpenSearch for logs"""
        try:
            if query is None:
                query = {
                    "query": {"match_all": {}},
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "size": size
                }
            
            url = f"{self.opensearch_url}/logs/_search"
            response = requests.post(url, json=query, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('hits', {}).get('hits', [])
        except Exception as e:
            logger.error(f"Error querying OpenSearch: {e}")
            return []

    def analyze_metrics(self) -> List[Dict]:
        """Analyze metrics for problems"""
        problems = []
        
        # Check error rate
        error_rate_query = 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])'
        error_rates = self.get_prometheus_metrics(error_rate_query)
        
        for result in error_rates:
            error_rate = float(result.get('value', [0, 0])[1])
            if error_rate > self.thresholds['error_rate']:
                problems.append({
                    'type': 'high_error_rate',
                    'severity': 'high',
                    'value': error_rate,
                    'threshold': self.thresholds['error_rate'],
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check claims rejection rate
        rejection_query = 'sum(claims_submitted_total{status="rejected"})'
        total_query = 'sum(claims_submitted_total)'
        
        rejections = self.get_prometheus_metrics(rejection_query)
        total_claims = self.get_prometheus_metrics(total_query)
        
        if rejections and total_claims:
            rejected_count = float(rejections[0].get('value', [0, 0])[1])
            total_count = float(total_claims[0].get('value', [0, 0])[1])
            
            if total_count > 0:
                rejection_rate = rejected_count / total_count
                
                if rejection_rate > 0.7:  # More than 70% rejected
                    problems.append({
                        'type': 'high_claim_rejection_rate',
                        'severity': 'high',
                        'value': rejection_rate * 100,
                        'rejected': int(rejected_count),
                        'total': int(total_count),
                        'timestamp': datetime.now().isoformat()
                    })
                elif rejection_rate > 0.5:  # More than 50% rejected
                    problems.append({
                        'type': 'high_claim_rejection_rate',
                        'severity': 'medium',
                        'value': rejection_rate * 100,
                        'rejected': int(rejected_count),
                        'total': int(total_count),
                        'timestamp': datetime.now().isoformat()
                    })
        
        # Check response time
        response_time_query = 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'
        response_times = self.get_prometheus_metrics(response_time_query)
        
        for result in response_times:
            response_time = float(result.get('value', [0, 0])[1]) * 1000  # Convert to ms
            if response_time > self.thresholds['response_time_p95']:
                problems.append({
                    'type': 'slow_response_time',
                    'severity': 'medium',
                    'value': response_time,
                    'threshold': self.thresholds['response_time_p95'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return problems

    def analyze_logs(self) -> List[Dict]:
        """Analyze logs for error patterns"""
        problems = []
        
        # Query for error logs
        error_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": "now-5m"}}},
                        {"match": {"level": "ERROR"}}
                    ]
                }
            },
            "size": 50
        }
        
        error_logs = self.get_opensearch_logs(error_query)
        
        if len(error_logs) > 10:  # More than 10 errors in 5 minutes
            problems.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'count': len(error_logs),
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for specific error patterns
        db_error_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": "now-5m"}}},
                        {"match": {"message": "database"}}
                    ]
                }
            },
            "size": 20
        }
        
        db_errors = self.get_opensearch_logs(db_error_query)
        if len(db_errors) > 5:
            problems.append({
                'type': 'database_connection_issues',
                'severity': 'high',
                'count': len(db_errors),
                'timestamp': datetime.now().isoformat()
            })
        
        return problems

    def generate_recommendations(self, problems: List[Dict]) -> List[Dict]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        for problem in problems:
            problem_type = problem['type']
            if problem_type in self.problem_patterns:
                pattern = self.problem_patterns[problem_type]
                recommendations.append({
                    'problem': pattern['description'],
                    'severity': problem['severity'],
                    'solutions': pattern['solutions'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return recommendations

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete analysis"""
        logger.info("Running observability analysis...")
        
        # Analyze metrics
        metric_problems = self.analyze_metrics()
        
        # Analyze logs
        log_problems = self.analyze_logs()
        
        # Combine all problems
        all_problems = metric_problems + log_problems
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_problems)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'problems': all_problems,
            'recommendations': recommendations,
            'summary': {
                'total_problems': len(all_problems),
                'high_severity': len([p for p in all_problems if p.get('severity') == 'high']),
                'medium_severity': len([p for p in all_problems if p.get('severity') == 'medium']),
                'low_severity': len([p for p in all_problems if p.get('severity') == 'low'])
            }
        }

# Global analyzer instance
analyzer = ObservabilityAnalyzer()

# Global correlation engine
correlation_engine = CorrelationEngine(
    prometheus_url=os.getenv('PROMETHEUS_URL', 'http://prometheus:9090'),
    opensearch_url=os.getenv('OPENSEARCH_URL', 'http://opensearch:9200'),
    jaeger_url=os.getenv('JAEGER_URL', 'http://jaeger:14268')
)

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/analysis')
def get_analysis():
    """Get current analysis results"""
    analysis = analyzer.run_analysis()
    return jsonify(analysis)

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    metrics = {
        'error_rate': analyzer.get_prometheus_metrics('rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])'),
        'response_time': analyzer.get_prometheus_metrics('histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'),
        'request_rate': analyzer.get_prometheus_metrics('rate(http_requests_total[5m])')
    }
    return jsonify(metrics)

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    logs = analyzer.get_opensearch_logs()
    return jsonify(logs)

@app.route('/api/correlation/story')
def get_correlation_story():
    """Get complete observability story with correlation"""
    story = correlation_engine.create_correlation_story()
    return jsonify(story)

@app.route('/api/correlation/rejection')
def get_rejection_correlation():
    """Deep dive into rejection patterns with correlation"""
    analysis = correlation_engine.correlate_claim_rejection_pattern()
    return jsonify(analysis)

@app.route('/api/correlation/errors')
def get_error_correlation():
    """Correlate error spikes across metrics, logs, traces"""
    analysis = correlation_engine.correlate_error_spike()
    return jsonify(analysis)

@app.route('/api/correlation/performance')
def get_performance_correlation():
    """Correlate performance issues"""
    analysis = correlation_engine.correlate_slow_requests()
    return jsonify(analysis)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
