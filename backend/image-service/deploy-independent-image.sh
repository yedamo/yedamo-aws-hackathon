#!/bin/bash

echo "🚀 Deploying Independent Saju Image Generation Service..."

STACK_NAME="saju-independent-image-service"
TEMPLATE_FILE="independent-image-service.yaml"

# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=StackPrefix,ParameterValue=saju-independent

echo "⏳ Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME

if [ $? -eq 0 ]; then
    echo "✅ Stack created successfully!"
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
      --stack-name $STACK_NAME \
      --query "Stacks[0].Outputs[?OutputKey=='IndependentImageApiUrl'].OutputValue" \
      --output text)
    
    echo "🔗 API Endpoint: $API_URL"
    echo "📝 Update your frontend to use this new endpoint"
    echo "💡 Update frontend/.env file: VITE_IMAGE_API_URL=$API_URL"
else
    echo "❌ Stack creation failed!"
    exit 1
fi
