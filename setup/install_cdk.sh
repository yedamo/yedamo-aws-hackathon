#!/bin/bash
echo "🚀 CDK 설치 시작"

# Node.js 설치
echo "📦 Node.js 설치..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CDK 설치
echo "🔧 AWS CDK 설치..."
sudo npm install -g aws-cdk

# 설치 확인
echo "✅ 설치 확인:"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "CDK: $(cdk --version)"

echo "🎉 CDK 설치 완료!"