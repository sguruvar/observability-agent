#!/usr/bin/env python3
"""
AWS Bedrock Insurance Claims Processing Agent - Instrumented Flask Application
With OpenTelemetry observability
"""

import os
import json
import uuid
import boto3
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.boto3sqs import Boto3SQSInstrumentor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry
def setup_observability():
    """Setup OpenTelemetry instrumentation"""
    
    # Create resource
    resource = Resource.create({
        "service.name": "insurance-claims-agent",
        "service.version": "1.0.0",
        "deployment.environment": os.getenv('NODE_ENV', 'development')
    })
    
    # Setup tracing
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv('JAEGER_AGENT_HOST', 'localhost'),
        agent_port=int(os.getenv('JAEGER_AGENT_PORT', '14268')),
    )
    
    # OTLP exporter for OpenSearch
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv('OTLP_ENDPOINT', 'http://localhost:4317'),
    )
    
    # Add span processors
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Setup metrics
    prometheus_reader = PrometheusMetricReader()
    meter_provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])
    
    # Instrument logging
    LoggingInstrumentor().instrument()
    
    return tracer

# Setup observability
tracer = setup_observability()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Instrument Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
Boto3SQSInstrumentor().instrument()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
ERROR_COUNT = Counter('http_errors_total', 'Total HTTP errors', ['error_type'])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize AWS clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
lambda_client = boto3.client('lambda', region_name=os.getenv('AWS_REGION', 'us-east-1'))
s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def upload_file_to_s3(file, bucket_name, key):
    """Upload file to S3 bucket with tracing"""
    with tracer.start_as_current_span("s3_upload") as span:
        span.set_attribute("s3.bucket", bucket_name)
        span.set_attribute("s3.key", key)
        
        try:
            s3_client.upload_fileobj(file, bucket_name, key)
            span.set_attribute("s3.upload.success", True)
            return f"s3://{bucket_name}/{key}"
        except ClientError as e:
            span.set_attribute("s3.upload.success", False)
            span.set_attribute("s3.upload.error", str(e))
            logger.error(f"Error uploading file to S3: {e}")
            raise

@app.route('/')
def index():
    """Serve the main page"""
    with tracer.start_as_current_span("serve_index"):
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
    """Submit a new insurance claim with full observability"""
    with tracer.start_as_current_span("submit_claim") as span:
        try:
            # Extract form data
            policy_number = request.form.get('policyNumber')
            claim_type = request.form.get('claimType')
            description = request.form.get('description')
            amount = float(request.form.get('amount', 0))
            contact_email = request.form.get('contactEmail')
            contact_phone = request.form.get('contactPhone', '')
            
            # Set span attributes
            span.set_attribute("claim.policy_number", policy_number)
            span.set_attribute("claim.type", claim_type)
            span.set_attribute("claim.amount", amount)
            
            # Generate claim ID
            claim_id = str(uuid.uuid4())
            span.set_attribute("claim.id", claim_id)
            
            # Handle file upload
            document_url = None
            if 'document' in request.files:
                file = request.files['document']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    s3_key = f"claims/{claim_id}/{filename}"
                    document_url = upload_file_to_s3(
                        file, 
                        os.getenv('S3_BUCKET_NAME'), 
                        s3_key
                    )
                    span.set_attribute("claim.document_uploaded", True)
            
            # Prepare claim data
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
                'documentUrl': document_url,
                'status': 'submitted',
                'submittedAt': datetime.utcnow().isoformat()
            }
            
            # Process claim using Lambda function
            with tracer.start_as_current_span("lambda_invoke") as lambda_span:
                lambda_span.set_attribute("lambda.function_name", os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'))
                
                lambda_response = lambda_client.invoke(
                    FunctionName=os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'),
                    Payload=json.dumps(claim_data)
                )
                
                result = json.loads(lambda_response['Payload'].read())
                lambda_span.set_attribute("lambda.response.status", result.get('status', 'unknown'))
            
            # Update metrics
            REQUEST_COUNT.labels(method='POST', endpoint='/api/claims/submit', status='200').inc()
            
            return jsonify({
                'success': True,
                'claimId': claim_id,
                'status': result.get('status', 'submitted'),
                'message': 'Claim submitted successfully'
            })
            
        except Exception as e:
            # Update error metrics
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
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
    """Get claim status by ID with tracing"""
    with tracer.start_as_current_span("get_claim") as span:
        span.set_attribute("claim.id", claim_id)
        
        try:
            # Query claim status using Lambda
            with tracer.start_as_current_span("lambda_invoke") as lambda_span:
                lambda_span.set_attribute("lambda.function_name", os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'))
                
                lambda_response = lambda_client.invoke(
                    FunctionName=os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'),
                    Payload=json.dumps({
                        'action': 'getClaim',
                        'claimId': claim_id
                    })
                )
                
                result = json.loads(lambda_response['Payload'].read())
            
            if result.get('success'):
                REQUEST_COUNT.labels(method='GET', endpoint='/api/claims/<id>', status='200').inc()
                return jsonify(result['data'])
            else:
                REQUEST_COUNT.labels(method='GET', endpoint='/api/claims/<id>', status='404').inc()
                return jsonify({'error': 'Claim not found'}), 404
                
        except Exception as e:
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            REQUEST_COUNT.labels(method='GET', endpoint='/api/claims/<id>', status='500').inc()
            
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            
            logger.error(f"Error fetching claim: {e}")
            return jsonify({'error': 'Failed to fetch claim status'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Bedrock agent about claims with tracing"""
    with tracer.start_as_current_span("chat_with_agent") as span:
        try:
            data = request.get_json()
            message = data.get('message')
            session_id = data.get('sessionId')
            
            span.set_attribute("chat.message_length", len(message) if message else 0)
            span.set_attribute("chat.session_id", session_id or "new")
            
            if not os.getenv('BEDROCK_AGENT_ID') or not os.getenv('BEDROCK_AGENT_ALIAS_ID'):
                return jsonify({'error': 'Bedrock agent not configured'}), 500
            
            # Invoke Bedrock agent
            with tracer.start_as_current_span("bedrock_invoke") as bedrock_span:
                bedrock_span.set_attribute("bedrock.agent_id", os.getenv('BEDROCK_AGENT_ID'))
                
                response = bedrock_agent_runtime.invoke_agent(
                    agentId=os.getenv('BEDROCK_AGENT_ID'),
                    agentAliasId=os.getenv('BEDROCK_AGENT_ALIAS_ID'),
                    sessionId=session_id or str(uuid.uuid4()),
                    inputText=message
                )
                
                # Read response
                response_text = ""
                for event in response['completion']:
                    if 'chunk' in event and 'bytes' in event['chunk']:
                        response_text += event['chunk']['bytes'].decode('utf-8')
                
                bedrock_span.set_attribute("bedrock.response_length", len(response_text))
            
            REQUEST_COUNT.labels(method='POST', endpoint='/api/chat', status='200').inc()
            
            return jsonify({
                'success': True,
                'response': response_text,
                'sessionId': response['sessionId']
            })
            
        except Exception as e:
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
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
    """Handle file too large error"""
    ERROR_COUNT.labels(error_type='FileTooLarge').inc()
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB.'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    ERROR_COUNT.labels(error_type='InternalError').inc()
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 Insurance Claims Agent (Instrumented) running on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"📈 Metrics: http://localhost:{port}/metrics")
    print(f"🌐 Application: http://localhost:{port}")
    print(f"🔍 Jaeger: http://localhost:16686")
    print(f"📊 Prometheus: http://localhost:9090")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
