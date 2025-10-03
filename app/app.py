#!/usr/bin/env python3
"""
AWS Bedrock Insurance Claims Processing Agent - Flask Application
"""

import os
import json
import uuid
import boto3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

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
    """Upload file to S3 bucket"""
    try:
        s3_client.upload_fileobj(file, bucket_name, key)
        return f"s3://{bucket_name}/{key}"
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/claims/submit', methods=['POST'])
def submit_claim():
    """Submit a new insurance claim"""
    try:
        # Extract form data
        policy_number = request.form.get('policyNumber')
        claim_type = request.form.get('claimType')
        description = request.form.get('description')
        amount = float(request.form.get('amount', 0))
        contact_email = request.form.get('contactEmail')
        contact_phone = request.form.get('contactPhone', '')
        
        # Generate claim ID
        claim_id = str(uuid.uuid4())
        
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
        lambda_response = lambda_client.invoke(
            FunctionName=os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'),
            Payload=json.dumps(claim_data)
        )
        
        result = json.loads(lambda_response['Payload'].read())
        
        return jsonify({
            'success': True,
            'claimId': claim_id,
            'status': result.get('status', 'submitted'),
            'message': 'Claim submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting claim: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit claim',
            'details': str(e)
        }), 500

@app.route('/api/claims/<claim_id>', methods=['GET'])
def get_claim(claim_id):
    """Get claim status by ID"""
    try:
        # Query claim status using Lambda
        lambda_response = lambda_client.invoke(
            FunctionName=os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'),
            Payload=json.dumps({
                'action': 'getClaim',
                'claimId': claim_id
            })
        )
        
        result = json.loads(lambda_response['Payload'].read())
        
        if result.get('success'):
            return jsonify(result['data'])
        else:
            return jsonify({'error': 'Claim not found'}), 404
            
    except Exception as e:
        logger.error(f"Error fetching claim: {e}")
        return jsonify({'error': 'Failed to fetch claim status'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Bedrock agent about claims"""
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('sessionId')
        
        if not os.getenv('BEDROCK_AGENT_ID') or not os.getenv('BEDROCK_AGENT_ALIAS_ID'):
            return jsonify({'error': 'Bedrock agent not configured'}), 500
        
        # Invoke Bedrock agent
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
        
        return jsonify({
            'success': True,
            'response': response_text,
            'sessionId': response['sessionId']
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process chat message',
            'details': str(e)
        }), 500

@app.route('/api/claims/<claim_id>/status', methods=['PUT'])
def update_claim_status(claim_id):
    """Update claim status (for manual review)"""
    try:
        data = request.get_json()
        
        lambda_response = lambda_client.invoke(
            FunctionName=os.getenv('CLAIMS_PROCESSING_LAMBDA_ARN'),
            Payload=json.dumps({
                'action': 'updateClaimStatus',
                'claimId': claim_id,
                'status': data.get('status'),
                'decision': data.get('decision'),
                'reasoning': data.get('reasoning')
            })
        )
        
        result = json.loads(lambda_response['Payload'].read())
        
        if result.get('success'):
            return jsonify({'message': 'Claim status updated successfully'})
        else:
            return jsonify({'error': result.get('error', 'Failed to update status')}), 400
            
    except Exception as e:
        logger.error(f"Error updating claim status: {e}")
        return jsonify({'error': 'Failed to update claim status'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB.'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 Insurance Claims Agent running on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🌐 Application: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
