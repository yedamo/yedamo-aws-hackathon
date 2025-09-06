FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 파일 복사
COPY package*.json ./
COPY yarn.lock ./

# 의존성 설치
RUN yarn install --production

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 3001

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# 애플리케이션 실행
CMD ["yarn", "start"]