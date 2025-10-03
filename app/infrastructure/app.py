#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_iam as iam,
    aws_bedrock as bedrock,
    aws_bedrockagent as bedrockagent,
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigateway,
    aws_logs as logs,
    Duration
)
from constructs import Construct

class InsuranceClaimsAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for storing claim documents
        self.claims_bucket = s3.Bucket(
            self, "ClaimsBucket",
            bucket_name=f"insurance-claims-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # DynamoDB Tables
        self.claims_table = dynamodb.Table(
            self, "ClaimsTable",
            table_name="insurance-claims",
            partition_key=dynamodb.Attribute(
                name="claimId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        self.policies_table = dynamodb.Table(
            self, "PoliciesTable",
            table_name="insurance-policies",
            partition_key=dynamodb.Attribute(
                name="policyNumber",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Lambda function for claims processing
        self.claims_processor_lambda = lambda_python.PythonFunction(
            self, "ClaimsProcessorLambda",
            function_name="insurance-claims-processor",
            entry="../lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="claims_processor.lambda_handler",
            timeout=Duration.minutes(5),
            memory_size=512,
            environment={
                "CLAIMS_TABLE": self.claims_table.table_name,
                "POLICIES_TABLE": self.policies_table.table_name,
                "S3_BUCKET_NAME": self.claims_bucket.bucket_name
            }
        )

        # Grant permissions to Lambda
        self.claims_table.grant_read_write_data(self.claims_processor_lambda)
        self.policies_table.grant_read_data(self.claims_processor_lambda)
        self.claims_bucket.grant_read_write(self.claims_processor_lambda)

        # Bedrock permissions for Lambda
        self.claims_processor_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )

        # Create Bedrock Knowledge Base
        self.knowledge_base = bedrockagent.CfnKnowledgeBase(
            self, "InsuranceKnowledgeBase",
            knowledge_base_configuration=bedrockagent.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrockagent.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v1"
                )
            ),
            name="insurance-knowledge-base",
            description="Knowledge base for insurance claims processing",
            role_arn=self.create_knowledge_base_role().role_arn,
            storage_configuration=bedrockagent.CfnKnowledgeBase.StorageConfigurationProperty(
                type="OPENSEARCH_SERVERLESS",
                opensearch_serverless_configuration=bedrockagent.CfnKnowledgeBase.OpenSearchServerlessConfigurationProperty(
                    collection_arn=f"arn:aws:aoss:{self.region}:{self.account}:collection/insurance-collection",
                    vector_index_name="insurance-index",
                    field_mapping=bedrockagent.CfnKnowledgeBase.VectorIndexConfigurationProperty(
                        vector_field="vector",
                        text_field="text",
                        metadata_field="metadata"
                    )
                )
            )
        )

        # Create Bedrock Agent
        self.bedrock_agent = bedrockagent.CfnAgent(
            self, "InsuranceAgent",
            agent_name="insurance-claims-agent",
            description="AI agent for processing insurance claims",
            foundation_model=f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="You are an AI assistant specialized in insurance claims processing. Help users with claim submissions, status checks, policy questions, and general insurance guidance. Be helpful, accurate, and professional.",
            agent_resource_role_arn=self.create_agent_role().role_arn,
            idle_session_ttl_in_seconds=1800
        )

        # Create Agent Alias
        self.agent_alias = bedrockagent.CfnAgentAlias(
            self, "InsuranceAgentAlias",
            agent_id=self.bedrock_agent.attr_agent_id,
            agent_alias_name="insurance-agent-alias",
            description="Production alias for insurance claims agent"
        )

        # Create API Gateway
        self.api = apigateway.RestApi(
            self, "InsuranceClaimsApi",
            rest_api_name="insurance-claims-api",
            description="API for insurance claims processing",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )

        # Lambda integration for API Gateway
        claims_lambda_integration = apigateway.LambdaIntegration(
            self.claims_processor_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )

        # API Gateway routes
        self.api.root.add_resource("claims").add_method("POST", claims_lambda_integration)
        self.api.root.add_resource("claims").add_resource("{claimId}").add_method("GET", claims_lambda_integration)

        # Outputs
        cdk.CfnOutput(
            self, "ClaimsBucketName",
            value=self.claims_bucket.bucket_name,
            description="S3 bucket for storing claim documents"
        )

        cdk.CfnOutput(
            self, "ClaimsTableName",
            value=self.claims_table.table_name,
            description="DynamoDB table for claims"
        )

        cdk.CfnOutput(
            self, "LambdaFunctionArn",
            value=self.claims_processor_lambda.function_arn,
            description="Lambda function ARN for claims processing"
        )

        cdk.CfnOutput(
            self, "BedrockAgentId",
            value=self.bedrock_agent.attr_agent_id,
            description="Bedrock Agent ID"
        )

        cdk.CfnOutput(
            self, "BedrockAgentAliasId",
            value=self.agent_alias.attr_agent_alias_id,
            description="Bedrock Agent Alias ID"
        )

        cdk.CfnOutput(
            self, "ApiGatewayUrl",
            value=self.api.url,
            description="API Gateway URL"
        )

    def create_knowledge_base_role(self):
        """Create IAM role for Bedrock Knowledge Base"""
        role = iam.Role(
            self, "KnowledgeBaseRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Role for Bedrock Knowledge Base"
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "aoss:APIAccessAll"
                ],
                resources=["*"]
            )
        )

        return role

    def create_agent_role(self):
        """Create IAM role for Bedrock Agent"""
        role = iam.Role(
            self, "AgentRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Role for Bedrock Agent"
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate"
                ],
                resources=["*"]
            )
        )

        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "lambda:InvokeFunction"
                ],
                resources=[self.claims_processor_lambda.function_arn]
            )
        )

        return role

app = cdk.App()
InsuranceClaimsAgentStack(app, "InsuranceClaimsAgentStack")
app.synth()
