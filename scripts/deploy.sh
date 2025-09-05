#!/bin/bash

# 배포 스크립트
set -e

echo "🚀 예다모 프론트엔드 배포 시작..."

# 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd frontend
yarn install
yarn build

# S3 업로드
echo "☁️ S3에 파일 업로드 중..."
aws s3 sync dist/ s3://yedamo-frontend-3si02day --delete --profile hackathon

# CloudFront 캐시 무효화
echo "🔄 CloudFront 캐시 무효화 중..."
aws cloudfront create-invalidation --distribution-id E1LD293UU79DMN --paths "/*" --profile hackathon

echo "✅ 배포 완료!"
echo "🌐 웹사이트 URL: https://do6x992wzv6m5.cloudfront.net"