#!/usr/bin/env python3
"""
Insurance Claims Processing Agent - Local Development Version
Runs without AWS services for testing the observability stack
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenSearch logging
try:
    from opensearch_handler import configure_opensearch_logging
    configure_opensearch_logging(logger, opensearch_url='http://localhost:9200')
    logger.info("OpenSearch logging configured successfully")
except Exception as e:
    logger.warning(f"Could not configure OpenSearch logging: {e}")

# In-memory storage for demo
claims_db = {}
policies_db = {
    'POL001': {'status': 'active', 'type': 'auto', 'coverage': 50000},
    'POL002': {'status': 'active', 'type': 'home', 'coverage': 250000},
    'POL003': {'status': 'active', 'type': 'health', 'coverage': 100000},
}

# Initialize OpenTelemetry
def setup_observability():
    """Setup OpenTelemetry instrumentation"""
    resource = Resource.create({
        "service.name": "insurance-claims-agent",
        "service.version": "1.0.0",
        "deployment.environment": "local"
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    # Use OTLP exporter for Jaeger (HTTP endpoint)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv('JAEGER_OTLP_ENDPOINT', 'http://localhost:4318/v1/traces'),
    )
    
    # Also add console exporter for debugging
    console_exporter = ConsoleSpanExporter()
    
    # Add both exporters
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(console_exporter))
    
    prometheus_reader = PrometheusMetricReader()
    meter_provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])
    
    return tracer

tracer = setup_observability()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Instrument Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
CLAIMS_SUBMITTED = Counter('claims_submitted_total', 'Total claims submitted', ['claim_type', 'status'])
CLAIMS_PROCESSING_TIME = Histogram('claims_processing_seconds', 'Claim processing time')
ACTIVE_CLAIMS = Gauge('active_claims_total', 'Number of active claims')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_claim_locally(claim_data):
    """Process claim locally without Lambda"""
    with tracer.start_as_current_span("process_claim_logic") as span:
        # Validate policy
        policy_number = claim_data['policyNumber']
        if policy_number not in policies_db:
            return {
                'status': 'rejected',
                'decision': 'rejected',
                'reasoning': 'Invalid or inactive policy number',
                'confidence': 100
            }
        
        policy = policies_db[policy_number]
        claim_amount = claim_data['amount']
        
        # Simple AI simulation
        span.set_attribute("policy.type", policy['type'])
        span.set_attribute("policy.coverage", policy['coverage'])
        
        # Decision logic
        confidence = random.randint(70, 95)
        
        if claim_amount > policy['coverage']:
            decision = 'rejected'
            reasoning = f"Claim amount (${claim_amount}) exceeds policy coverage (${policy['coverage']})"
            status = 'rejected'
        elif claim_amount < 1000:
            decision = 'approved'
            reasoning = "Low-value claim automatically approved"
            status = 'approved'
        elif confidence >= 80:
            decision = 'approved'
            reasoning = "Claim meets all criteria for automatic approval"
            status = 'approved'
        else:
            decision = 'pending'
            reasoning = "Claim requires manual review"
            status = 'pending_review'
        
        return {
            'status': status,
            'decision': decision,
            'reasoning': reasoning,
            'confidence': confidence,
            'processedAt': datetime.utcnow().isoformat()
        }

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    with tracer.start_as_current_span("health_check"):
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/claims/submit', methods=['POST'])
def submit_claim():
    """Submit a new insurance claim"""
    with tracer.start_as_current_span("submit_claim") as span:
        with CLAIMS_PROCESSING_TIME.time():
            try:
                # Extract form data
                policy_number = request.form.get('policyNumber')
                claim_type = request.form.get('claimType')
                description = request.form.get('description')
                amount = float(request.form.get('amount', 0))
                contact_email = request.form.get('contactEmail')
                contact_phone = request.form.get('contactPhone', '')
                
                span.set_attribute("claim.policy_number", policy_number)
                span.set_attribute("claim.type", claim_type)
                span.set_attribute("claim.amount", amount)
                
                claim_id = str(uuid.uuid4())
                span.set_attribute("claim.id", claim_id)
                
                # Handle file upload
                document_path = None
                if 'document' in request.files:
                    file = request.files['document']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{claim_id}_{filename}")
                        file.save(filepath)
                        document_path = filepath
                        span.set_attribute("claim.document_uploaded", True)
                
                # Create claim data
                claim_data = {
                    'claimId': claim_id,
                    'policyNumber': policy_number,
                    'claimType': claim_type,
                    'description': description,
                    'amount': amount,
                    'contactInfo': {
                        'email': contact_email,
                        'phone': contact_phone
                    },
                    'documentPath': document_path,
                    'submittedAt': datetime.utcnow().isoformat()
                }
                
                # Process claim locally
                result = process_claim_locally(claim_data)
                claim_data.update(result)
                
                # Store in memory
                claims_db[claim_id] = claim_data
                
                # Update metrics
                REQUEST_COUNT.labels(method='POST', endpoint='/api/claims/submit', status='200').inc()
                CLAIMS_SUBMITTED.labels(claim_type=claim_type, status=result['status']).inc()
                ACTIVE_CLAIMS.set(len([c for c in claims_db.values() if c.get('status') == 'pending_review']))
                
                logger.info(f"Claim {claim_id} submitted and processed: {result['status']}")
                
                return jsonify({
                    'success': True,
                    'claimId': claim_id,
                    'status': result['status'],
                    'decision': result['decision'],
                    'reasoning': result['reasoning'],
                    'confidence': result['confidence'],
                    'message': 'Claim submitted successfully'
                })
                
            except Exception as e:
                REQUEST_COUNT.labels(method='POST', endpoint='/api/claims/submit', status='500').inc()
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                logger.error(f"Error submitting claim: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to submit claim',
                    'details': str(e)
                }), 500

@app.route('/api/claims/<claim_id>', methods=['GET'])
def get_claim(claim_id):
    """Get claim status by ID"""
    with tracer.start_as_current_span("get_claim") as span:
        span.set_attribute("claim.id", claim_id)
        
        try:
            if claim_id in claims_db:
                REQUEST_COUNT.labels(method='GET', endpoint='/api/claims/<id>', status='200').inc()
                return jsonify(claims_db[claim_id])
            else:
                REQUEST_COUNT.labels(method='GET', endpoint='/api/claims/<id>', status='404').inc()
                return jsonify({'error': 'Claim not found'}), 404
                
        except Exception as e:
            REQUEST_COUNT.labels(method='GET', endpoint='/api/claims/<id>', status='500').inc()
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            logger.error(f"Error fetching claim: {e}")
            return jsonify({'error': 'Failed to fetch claim status'}), 500

@app.route('/api/claims', methods=['GET'])
def list_claims():
    """List all claims"""
    with tracer.start_as_current_span("list_claims"):
        return jsonify({
            'success': True,
            'claims': list(claims_db.values()),
            'total': len(claims_db)
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint (no Bedrock required for local dev)"""
    with tracer.start_as_current_span("chat_with_agent") as span:
        try:
            data = request.get_json()
            message = data.get('message', '')
            
            span.set_attribute("chat.message_length", len(message))
            
            # Simple mock responses
            responses = {
                'status': f"You have {len(claims_db)} total claims. {len([c for c in claims_db.values() if c.get('status') == 'pending_review'])} pending review.",
                'help': "I can help you with: 1) Submitting claims, 2) Checking claim status, 3) Understanding your policy coverage.",
                'default': "I'm a demo AI assistant. In production, I would connect to AWS Bedrock for intelligent responses."
            }
            
            response_text = responses.get('default', responses['default'])
            if 'status' in message.lower() or 'how many' in message.lower():
                response_text = responses['status']
            elif 'help' in message.lower():
                response_text = responses['help']
            
            REQUEST_COUNT.labels(method='POST', endpoint='/api/chat', status='200').inc()
            
            return jsonify({
                'success': True,
                'response': response_text,
                'sessionId': str(uuid.uuid4())
            })
            
        except Exception as e:
            REQUEST_COUNT.labels(method='POST', endpoint='/api/chat', status='500').inc()
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            logger.error(f"Error in chat: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to process chat message',
                'details': str(e)
            }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB.'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3002))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 Insurance Claims Agent (Local Dev) running on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"📈 Metrics: http://localhost:{port}/metrics")
    print(f"🌐 Application: http://localhost:{port}")
    print(f"🔍 Jaeger: http://localhost:16686")
    print(f"📊 Prometheus: http://localhost:9090")
    print(f"🤖 AI Dashboard: http://localhost:8000")
    print("")
    print("💡 This is a local development version without AWS dependencies")
    print("   Claims are processed in-memory for testing the observability stack")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
