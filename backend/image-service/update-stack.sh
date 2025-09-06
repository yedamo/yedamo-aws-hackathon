#!/bin/bash

echo "🔄 Updating Independent Saju Image Generation Service..."

STACK_NAME="saju-independent-image-service"
TEMPLATE_FILE="independent-image-service.yaml"

# Update CloudFormation stack
aws cloudformation update-stack \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=StackPrefix,ParameterValue=saju-independent

echo "⏳ Waiting for stack update to complete..."
aws cloudformation wait stack-update-complete --stack-name $STACK_NAME

if [ $? -eq 0 ]; then
    echo "✅ Stack updated successfully!"
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
      --stack-name $STACK_NAME \
      --query "Stacks[0].Outputs[?OutputKey=='IndependentImageApiUrl'].OutputValue" \
      --output text)
    
    echo "🔗 API Endpoint: $API_URL"
    echo "💡 Update frontend/.env file: VITE_IMAGE_API_URL=$API_URL"
else
    echo "❌ Stack update failed!"
    exit 1
fi
