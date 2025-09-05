# 예다모 프론트엔드 배포 가이드

## 개요
React + Vite 기반의 AI 사주 상담사 프론트엔드를 AWS S3 + CloudFront로 배포하는 가이드입니다.

## 배포 아키텍처
```
GitHub → Build → S3 (Static Hosting) → CloudFront (CDN) → Users
```

## 사전 준비

### 1. AWS CLI 설정
```bash
# AWS CLI 설치 (macOS)
brew install awscli

# hackathon 프로필 설정
aws configure set aws_access_key_id YOUR_ACCESS_KEY --profile hackathon
aws configure set aws_secret_access_key YOUR_SECRET_KEY --profile hackathon
aws configure set region us-east-1 --profile hackathon
```

### 2. Terraform 설치
```bash
brew install terraform
```

## 인프라 배포

### 1. Terraform 초기화 및 배포
```bash
cd ../infrastructure
terraform init
terraform plan
terraform apply -auto-approve
```

### 2. 배포 결과 확인
```bash
terraform output
```

## 프론트엔드 배포

### 1. 의존성 설치 및 빌드
```bash
yarn install
yarn build
```

### 2. S3 업로드
```bash
aws s3 sync dist/ s3://BUCKET_NAME --delete --profile hackathon
```

### 3. CloudFront 캐시 무효화
```bash
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*" --profile hackathon
```

## 자동 배포 스크립트

프로젝트 루트의 `deploy.sh` 스크립트를 사용하여 원클릭 배포:

```bash
cd ..
./deploy.sh
```

## 현재 배포 정보

- **S3 버킷**: `yedamo-frontend-3si02day`
- **CloudFront 배포 ID**: `E1LD293UU79DMN`
- **웹사이트 URL**: https://do6x992wzv6m5.cloudfront.net

## 리소스 삭제

```bash
cd ../infrastructure
terraform destroy -auto-approve
```

## 개발 환경

### 로컬 개발 서버 실행
```bash
yarn dev
```

### 빌드 테스트
```bash
yarn build
yarn preview
```

## CI/CD 파이프라인

### 자동 배포
- **GitHub** → **CodeBuild** → **S3** → **CloudFront**
- `main` 브랜치 푸시 시 자동 빌드 및 배포
- CodeBuild 프로젝트: `yedamo-frontend-build`

### 수동 배포
```bash
# 로컬에서 직접 배포
./deploy.sh

# CodeBuild 수동 트리거
aws codebuild start-build --project-name yedamo-frontend-build --profile hackathon
```

## 기술 스택

- **Frontend**: React 18, Vite, Tailwind CSS
- **Infrastructure**: Terraform, AWS S3, CloudFront
- **CI/CD**: AWS CodeBuild, GitHub Webhooks