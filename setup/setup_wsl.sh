#!/bin/bash
# WSL 환경에서 AWS 배포 환경 설정

echo "🚀 WSL AWS 배포 환경 설정 시작"

# 패키지 업데이트
echo "📦 패키지 업데이트..."
sudo apt update

# AWS CLI v2 설치
echo "☁️ AWS CLI 설치..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Node.js 설치
echo "📦 Node.js 설치..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CDK 설치
echo "🔧 AWS CDK 설치..."
sudo npm install -g aws-cdk

# Python 설치
echo "🐍 Python 환경 설정..."
sudo apt install python3.11 python3.11-venv python3-pip -y

# 설치 확인
echo "✅ 설치 확인:"
echo "AWS CLI: $(aws --version)"
echo "Node.js: $(node --version)"
echo "CDK: $(cdk --version)"
echo "Python: $(python3.11 --version)"

echo ""
echo "🎉 설치 완료!"
echo "다음 단계:"
echo "1. aws configure 실행하여 계정 연결"
echo "2. python3 deploy.py 실행하여 배포"