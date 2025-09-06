#!/bin/bash

echo "🚀 Deploying/Updating Independent Saju Image Generation Service..."

STACK_NAME="saju-independent-image-service"

# Check if stack exists
aws cloudformation describe-stacks --stack-name $STACK_NAME > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "📦 Stack exists. Updating..."
    ./update-stack.sh
else
    echo "🆕 Stack doesn't exist. Creating..."
    ./deploy-independent-image.sh
fi
