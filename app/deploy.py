#!/usr/bin/env python3
"""
AWS Bedrock Insurance Claims Agent - Python Deployment Script
"""

import os
import sys
import subprocess
import json
import boto3
from botocore.exceptions import ClientError
import time

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def check_aws_cli():
    """Check if AWS CLI is installed and configured"""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, check=True)
        identity = json.loads(result.stdout)
        print(f"✅ AWS CLI configured for account: {identity.get('Account')}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ AWS CLI not found or not configured")
        print("Please install AWS CLI and run 'aws configure'")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    run_command("pip install -r requirements.txt")
    print("✅ Python dependencies installed")

def install_cdk():
    """Install AWS CDK if not already installed"""
    try:
        run_command("cdk --version")
        print("✅ AWS CDK already installed")
    except subprocess.CalledProcessError:
        print("📦 Installing AWS CDK...")
        run_command("pip install aws-cdk")
        print("✅ AWS CDK installed")

def deploy_infrastructure():
    """Deploy AWS infrastructure using CDK"""
    print("🏗️ Deploying infrastructure...")
    
    # Change to infrastructure directory
    infra_dir = os.path.join(os.path.dirname(__file__), 'infrastructure')
    
    # Install infrastructure dependencies
    print("📦 Installing infrastructure dependencies...")
    run_command("pip install -r requirements.txt", cwd=infra_dir)
    
    # Bootstrap CDK if needed
    print("🔧 Bootstrapping CDK...")
    run_command("cdk bootstrap", cwd=infra_dir)
    
    # Deploy the stack
    print("🚀 Deploying CDK stack...")
    run_command("cdk deploy --require-approval never", cwd=infra_dir)
    
    print("✅ Infrastructure deployed successfully")

def get_stack_outputs():
    """Get stack outputs from CloudFormation"""
    try:
        cf_client = boto3.client('cloudformation')
        response = cf_client.describe_stacks(StackName='InsuranceClaimsAgentStack')
        
        outputs = {}
        for output in response['Stacks'][0]['Outputs']:
            outputs[output['OutputKey']] = output['OutputValue']
        
        return outputs
    except ClientError as e:
        print(f"❌ Error getting stack outputs: {e}")
        return {}

def create_env_file(outputs):
    """Create .env file with stack outputs"""
    print("📝 Creating environment configuration...")
    
    env_content = f"""# AWS Configuration
AWS_REGION={boto3.Session().region_name or 'us-east-1'}
AWS_ACCESS_KEY_ID={os.getenv('AWS_ACCESS_KEY_ID', 'your_access_key_here')}
AWS_SECRET_ACCESS_KEY={os.getenv('AWS_SECRET_ACCESS_KEY', 'your_secret_key_here')}

# Bedrock Agent Configuration
BEDROCK_AGENT_ID={outputs.get('BedrockAgentId', 'your_agent_id_here')}
BEDROCK_AGENT_ALIAS_ID={outputs.get('BedrockAgentAliasId', 'your_alias_id_here')}
BEDROCK_KNOWLEDGE_BASE_ID=your_kb_id_here

# Lambda Configuration
CLAIMS_PROCESSING_LAMBDA_ARN={outputs.get('LambdaFunctionArn', 'your_lambda_arn_here')}

# S3 Configuration
S3_BUCKET_NAME={outputs.get('ClaimsBucketName', 'your_bucket_name_here')}

# Application Configuration
PORT=3000
NODE_ENV=production
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created")

def populate_sample_data(outputs):
    """Populate DynamoDB with sample data"""
    print("📊 Populating sample insurance policies...")
    
    try:
        dynamodb = boto3.resource('dynamodb')
        policies_table = dynamodb.Table(outputs.get('PoliciesTableName', 'insurance-policies'))
        
        # Sample policies
        sample_policies = [
            {
                'policyNumber': 'POL001',
                'status': 'active',
                'policyType': 'auto',
                'coverageAmount': 50000,
                'premium': 1200,
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'customerName': 'John Doe',
                'customerEmail': 'john.doe@example.com'
            },
            {
                'policyNumber': 'POL002',
                'status': 'active',
                'policyType': 'home',
                'coverageAmount': 250000,
                'premium': 800,
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'customerName': 'Jane Smith',
                'customerEmail': 'jane.smith@example.com'
            },
            {
                'policyNumber': 'POL003',
                'status': 'active',
                'policyType': 'health',
                'coverageAmount': 100000,
                'premium': 300,
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'customerName': 'Bob Johnson',
                'customerEmail': 'bob.johnson@example.com'
            }
        ]
        
        for policy in sample_policies:
            policies_table.put_item(Item=policy)
        
        print("✅ Sample policies populated")
        
    except Exception as e:
        print(f"⚠️ Could not populate sample policies: {e}")

def start_application():
    """Start the Flask application"""
    print("🎉 Deployment completed successfully!")
    print("")
    print("📋 Configuration Summary:")
    print("   Application: Python Flask")
    print("   Port: 3000")
    print("   Health check: http://localhost:3000/health")
    print("   Application: http://localhost:3000")
    print("")
    print("🚀 Starting the application...")
    print("   Press Ctrl+C to stop the application")
    print("")
    
    # Start the Flask application
    try:
        run_command("python app.py")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")

def main():
    """Main deployment function"""
    print("🚀 Starting deployment of AWS Bedrock Insurance Claims Agent (Python)")
    print("=" * 70)
    
    # Check prerequisites
    if not check_aws_cli():
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Install CDK
    install_cdk()
    
    # Deploy infrastructure
    deploy_infrastructure()
    
    # Get stack outputs
    outputs = get_stack_outputs()
    if not outputs:
        print("❌ Failed to get stack outputs")
        sys.exit(1)
    
    # Create environment file
    create_env_file(outputs)
    
    # Populate sample data
    populate_sample_data(outputs)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
