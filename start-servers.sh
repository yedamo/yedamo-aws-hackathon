#!/bin/bash

echo "예다모 서버 시작 스크립트"
echo "========================"

# 백엔드 의존성 설치 및 서버 시작
echo "1. 백엔드 서버 시작 중..."
cd backend
npm install
npm start &
BACKEND_PID=$!

# 잠시 대기
sleep 3

# 프론트엔드 서버 시작
echo "2. 프론트엔드 서버 시작 중..."
cd ../frontend
yarn install
yarn dev &
FRONTEND_PID=$!

echo ""
echo "서버가 시작되었습니다!"
echo "- 백엔드: http://localhost:3001"
echo "- 프론트엔드: http://localhost:3000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."

# 종료 시그널 처리
trap "echo '서버를 종료합니다...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 백그라운드 프로세스 대기
wait