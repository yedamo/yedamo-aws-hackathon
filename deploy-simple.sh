#!/bin/bash

echo "🚀 간단한 이미지 생성 서비스 배포..."

# Lambda 함수 생성
echo "📦 Lambda 함수 생성..."
aws lambda create-function \
    --function-name yedamo-image-generator \
    --runtime python3.11 \
    --role arn:aws:iam::975050110318:role/lambda-execution-role \
    --handler image_generator.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 120 \
    --memory-size 1024 \
    --region us-east-1 || echo "함수가 이미 존재합니다."

# API Gateway 생성
echo "🌐 API Gateway 생성..."
API_ID=$(aws apigateway create-rest-api \
    --name yedamo-image-api \
    --region us-east-1 \
    --query 'id' --output text)

echo "API ID: $API_ID"

# 리소스 생성
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region us-east-1 \
    --query 'items[0].id' --output text)

RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part image \
    --region us-east-1 \
    --query 'id' --output text)

# POST 메서드 생성
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region us-east-1

# Lambda 통합 설정
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:975050110318:function:yedamo-image-generator/invocations \
    --region us-east-1

# 배포
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region us-east-1

echo "✅ 배포 완료!"
echo "🌐 API URL: https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/image"
