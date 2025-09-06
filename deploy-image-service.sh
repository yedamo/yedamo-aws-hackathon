#!/bin/bash

echo "🚀 Bedrock Nova Pro 이미지 생성 서비스 배포 시작..."

# 프로젝트 디렉토리로 이동
cd /Users/sulmo/dev/yedamo-aws-hackathon

# CDK 디렉토리로 이동
cd cdk

# Python 가상환경 활성화
echo "📦 Python 가상환경 활성화..."
source venv/bin/activate

# 의존성 설치
echo "📦 의존성 설치..."
pip install -r requirements.txt

# CDK 부트스트랩 (처음 배포시에만 필요)
echo "🔧 CDK 부트스트랩 확인..."
cdk bootstrap

# CDK 배포
echo "🚀 CDK 스택 배포..."
cdk deploy --require-approval never

echo "✅ 배포 완료!"
echo ""
echo "📋 API 엔드포인트:"
echo "POST /image - 이미지 생성"
echo ""
echo "📝 사용 예시:"
echo 'curl -X POST https://YOUR_API_URL/prod/image \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"color": "빨간", "animal": "용"}'"'"''
echo ""
echo "🐉 지원되는 12지신 동물:"
echo "쥐, 소, 호랑이, 토끼, 용, 뱀, 말, 양, 원숭이, 닭, 개, 돼지"
