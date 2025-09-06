#!/bin/bash

echo "🚀 직접 AWS CLI로 이미지 생성 서비스 배포..."

# 1. IAM Role 생성
echo "📋 IAM Role 생성..."
aws iam create-role \
    --role-name yedamo-image-generator-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' \
    --region us-east-1 || echo "Role이 이미 존재합니다."

# 2. IAM Policy 연결
echo "🔐 IAM Policy 연결..."
aws iam attach-role-policy \
    --role-name yedamo-image-generator-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    --region us-east-1

aws iam put-role-policy \
    --role-name yedamo-image-generator-role \
    --policy-name BedrockAccess \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "bedrock:InvokeModel",
                "Resource": "*"
            }
        ]
    }' \
    --region us-east-1

# 3. Lambda 함수 생성
echo "⚡ Lambda 함수 생성..."
cd /Users/sulmo/dev/yedamo-aws-hackathon/lambda

aws lambda create-function \
    --function-name yedamo-image-generator \
    --runtime python3.11 \
    --role arn:aws:iam::975050110318:role/yedamo-image-generator-role \
    --handler image_generator.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 120 \
    --memory-size 1024 \
    --region us-east-1 || \
aws lambda update-function-code \
    --function-name yedamo-image-generator \
    --zip-file fileb://lambda-deployment.zip \
    --region us-east-1

# 4. API Gateway 생성
echo "🌐 API Gateway 생성..."
API_ID=$(aws apigateway create-rest-api \
    --name yedamo-image-api \
    --region us-east-1 \
    --query 'id' --output text 2>/dev/null || \
    aws apigateway get-rest-apis \
    --region us-east-1 \
    --query 'items[?name==`yedamo-image-api`].id' --output text)

echo "API ID: $API_ID"

# 5. 리소스 생성
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region us-east-1 \
    --query 'items[0].id' --output text)

RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part image \
    --region us-east-1 \
    --query 'id' --output text 2>/dev/null || \
    aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region us-east-1 \
    --query 'items[?pathPart==`image`].id' --output text)

# 6. POST 메서드 생성
echo "📡 POST 메서드 생성..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region us-east-1

# 7. Lambda 통합 설정
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:975050110318:function:yedamo-image-generator/invocations \
    --region us-east-1

# 8. Lambda 권한 부여
echo "🔑 Lambda 권한 부여..."
aws lambda add-permission \
    --function-name yedamo-image-generator \
    --statement-id api-gateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:975050110318:$API_ID/*/*" \
    --region us-east-1 || echo "권한이 이미 존재합니다."

# 9. 배포
echo "🚀 API 배포..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region us-east-1

echo ""
echo "✅ 배포 완료!"
echo "🌐 API URL: https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/image"
echo ""
echo "📝 테스트 명령어:"
echo "curl -X POST https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/image \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"color\": \"빨간\", \"animal\": \"용\"}'"
