# EC2 백엔드 수동 배포 가이드

## 1. EC2 접속
```bash
ssh -i yedamo-key-pair.pem ec2-user@34.201.100.228
```

## 2. 환경 확인
```bash
# Node.js 설치 확인
node --version
npm --version
pm2 --version

# 환경변수 확인
echo $REDIS_HOST
cat ~/.bashrc | grep export
```

## 3. 프로젝트 클론
```bash
cd /home/ec2-user
git clone https://github.com/your-username/yedamo-aws-hackathon.git
cd yedamo-aws-hackathon/backend
```

## 4. 백엔드 시작
```bash
# 자동 생성된 스크립트 실행
./start-backend.sh

# 또는 수동 실행
export REDIS_HOST=yed-ye-s1e8rclk1mpj.9vjq7o.0001.use1.cache.amazonaws.com
export REDIS_PORT=6379
export AWS_REGION=us-east-1
export PORT=3001
npm install
pm2 start server.js --name yedamo-backend
pm2 save
pm2 startup
```

## 5. 서버 상태 확인
```bash
pm2 status
curl http://localhost:3001/health
```

## 배포된 리소스 정보
- **API Gateway**: https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod/
- **Backend Server**: http://34.201.100.228:3001
- **Redis Host**: yed-ye-s1e8rclk1mpj.9vjq7o.0001.use1.cache.amazonaws.com
- **EC2 Public IP**: 34.201.100.228

## API 테스트
```bash
# 헬스체크
curl http://34.201.100.228:3001/health

# 사주 기본 분석 (직접 EC2)
curl -X POST http://34.201.100.228:3001/saju/basic \
  -H "Content-Type: application/json" \
  -d '{
    "birthDate": "1990-05-15",
    "birthTime": "14:00",
    "isLunar": false,
    "gender": "male",
    "name": "김다롬"
  }'

# 상담 API (직접 EC2)
curl -X POST http://34.201.100.228:3001/saju/consultation \
  -H "Content-Type: application/json" \
  -d '{
    "cache_key": "CACHE_KEY_FROM_BASIC_API",
    "question": "올해 운세는 어떤가요?"
  }'

# API Gateway를 통한 테스트
curl -X POST https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod/saju/basic \
  -H "Content-Type: application/json" \
  -d '{
    "birth_info": {
      "year": 1990,
      "month": 5,
      "day": 15,
      "hour": 14
    },
    "name": "김다롬"
  }'
```
