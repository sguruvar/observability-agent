import json
import boto3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime')

# Environment variables
CLAIMS_TABLE = os.environ.get('CLAIMS_TABLE', 'insurance-claims')
POLICIES_TABLE = os.environ.get('POLICIES_TABLE', 'insurance-policies')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'insurance-claims-bucket')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for insurance claims processing
    """
    try:
        action = event.get('action', 'processClaim')
        
        if action == 'processClaim':
            return process_claim(event)
        elif action == 'getClaim':
            return get_claim(event.get('claimId'))
        elif action == 'updateClaimStatus':
            return update_claim_status(event)
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }
            
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def process_claim(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a new insurance claim
    """
    try:
        # Extract claim data
        claim_data = {
            'claimId': event.get('claimId'),
            'policyNumber': event.get('policyNumber'),
            'claimType': event.get('claimType'),
            'description': event.get('description'),
            'amount': float(event.get('amount', 0)),
            'contactInfo': event.get('contactInfo', {}),
            'documentUrl': event.get('documentUrl'),
            'status': 'submitted',
            'submittedAt': event.get('submittedAt', datetime.utcnow().isoformat()),
            'processedAt': None,
            'decision': None,
            'reasoning': None
        }
        
        # Validate policy
        policy_valid = validate_policy(claim_data['policyNumber'])
        if not policy_valid:
            claim_data['status'] = 'rejected'
            claim_data['decision'] = 'rejected'
            claim_data['reasoning'] = 'Invalid or inactive policy number'
            claim_data['processedAt'] = datetime.utcnow().isoformat()
        else:
            # Use AI to analyze claim
            ai_analysis = analyze_claim_with_ai(claim_data)
            claim_data.update(ai_analysis)
        
        # Store claim in DynamoDB
        store_claim(claim_data)
        
        return {
            'success': True,
            'claimId': claim_data['claimId'],
            'status': claim_data['status'],
            'decision': claim_data['decision'],
            'reasoning': claim_data['reasoning']
        }
        
    except Exception as e:
        print(f"Error processing claim: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def validate_policy(policy_number: str) -> bool:
    """
    Validate if policy number exists and is active
    """
    try:
        table = dynamodb.Table(POLICIES_TABLE)
        response = table.get_item(Key={'policyNumber': policy_number})
        
        if 'Item' in response:
            policy = response['Item']
            return policy.get('status') == 'active'
        return False
        
    except Exception as e:
        print(f"Error validating policy: {str(e)}")
        return False

def analyze_claim_with_ai(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Bedrock AI to analyze the claim and make a decision
    """
    try:
        # Prepare prompt for AI analysis
        prompt = f"""
        Analyze this insurance claim and provide a decision with reasoning:
        
        Policy Number: {claim_data['policyNumber']}
        Claim Type: {claim_data['claimType']}
        Description: {claim_data['description']}
        Amount: ${claim_data['amount']}
        
        Please provide:
        1. Decision: APPROVED, REJECTED, or PENDING_REVIEW
        2. Confidence Score: 0-100
        3. Reasoning: Detailed explanation of the decision
        4. Risk Factors: Any concerns or red flags
        5. Recommendations: Next steps or additional documentation needed
        
        Respond in JSON format.
        """
        
        # Call Bedrock Claude model
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'prompt': prompt,
                'max_tokens_to_sample': 1000,
                'temperature': 0.1
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['completion']
        
        # Parse AI response
        try:
            ai_data = json.loads(ai_response)
            decision = ai_data.get('Decision', 'PENDING_REVIEW')
            confidence = ai_data.get('Confidence Score', 50)
            reasoning = ai_data.get('Reasoning', 'AI analysis completed')
            risk_factors = ai_data.get('Risk Factors', [])
            recommendations = ai_data.get('Recommendations', [])
        except:
            # Fallback if JSON parsing fails
            decision = 'PENDING_REVIEW'
            confidence = 50
            reasoning = ai_response
            risk_factors = []
            recommendations = []
        
        # Determine final status based on AI decision and confidence
        if decision == 'APPROVED' and confidence >= 80:
            status = 'approved'
        elif decision == 'REJECTED' and confidence >= 70:
            status = 'rejected'
        else:
            status = 'pending_review'
        
        return {
            'status': status,
            'decision': decision.lower(),
            'reasoning': reasoning,
            'confidence': confidence,
            'riskFactors': risk_factors,
            'recommendations': recommendations,
            'processedAt': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return {
            'status': 'pending_review',
            'decision': 'pending',
            'reasoning': f'AI analysis failed: {str(e)}',
            'confidence': 0,
            'riskFactors': [],
            'recommendations': ['Manual review required'],
            'processedAt': datetime.utcnow().isoformat()
        }

def store_claim(claim_data: Dict[str, Any]) -> None:
    """
    Store claim data in DynamoDB
    """
    try:
        table = dynamodb.Table(CLAIMS_TABLE)
        table.put_item(Item=claim_data)
    except Exception as e:
        print(f"Error storing claim: {str(e)}")
        raise

def get_claim(claim_id: str) -> Dict[str, Any]:
    """
    Retrieve claim data from DynamoDB
    """
    try:
        table = dynamodb.Table(CLAIMS_TABLE)
        response = table.get_item(Key={'claimId': claim_id})
        
        if 'Item' in response:
            return {
                'success': True,
                'data': response['Item']
            }
        else:
            return {
                'success': False,
                'error': 'Claim not found'
            }
            
    except Exception as e:
        print(f"Error retrieving claim: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def update_claim_status(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update claim status (for manual review)
    """
    try:
        claim_id = event.get('claimId')
        new_status = event.get('status')
        decision = event.get('decision')
        reasoning = event.get('reasoning')
        
        table = dynamodb.Table(CLAIMS_TABLE)
        
        update_expression = "SET #status = :status, processedAt = :processedAt"
        expression_attribute_names = {"#status": "status"}
        expression_attribute_values = {
            ":status": new_status,
            ":processedAt": datetime.utcnow().isoformat()
        }
        
        if decision:
            update_expression += ", #decision = :decision"
            expression_attribute_names["#decision"] = "decision"
            expression_attribute_values[":decision"] = decision
            
        if reasoning:
            update_expression += ", reasoning = :reasoning"
            expression_attribute_values[":reasoning"] = reasoning
        
        table.update_item(
            Key={'claimId': claim_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        return {
            'success': True,
            'message': 'Claim status updated successfully'
        }
        
    except Exception as e:
        print(f"Error updating claim status: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
