#!/bin/bash

# EC2 배포 스크립트
BACKEND_IP="34.207.181.21"
KEY_PATH="/mnt/c/Users/ekfha/vscode/yedamo-aws-hackathon/yedamo-key-pair.pem"
REDIS_HOST="yed-ye-s1e8rclk1mpj.9vjq7o.0001.use1.cache.amazonaws.com"

echo "🚀 EC2 백엔드 서버 배포 시작..."

# 1. 코드 업데이트
echo "📦 코드 업데이트 중..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ubuntu@$BACKEND_IP << 'EOF'
cd /home/ubuntu/yedamo-aws-hackathon
git pull origin main
EOF

# 2. 백엔드 의존성 설치 및 환경변수 설정
echo "🔧 백엔드 설정 중..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ubuntu@$BACKEND_IP << EOF
cd /home/ubuntu/yedamo-aws-hackathon/backend

# 환경변수 설정
export REDIS_HOST="$REDIS_HOST"
export REDIS_PORT="6379"
export AWS_REGION="us-east-1"
export PORT="3001"

# 의존성 설치
npm install

# PM2로 서버 재시작
pm2 stop all || true
pm2 start server.js --name "yedamo-backend"
pm2 save
pm2 startup

echo "✅ 백엔드 서버 시작 완료"
pm2 status
EOF

echo "🎉 배포 완료!"
echo "📍 백엔드 서버: http://$BACKEND_IP:3001"
echo "🔍 헬스체크: http://$BACKEND_IP:3001/health"
