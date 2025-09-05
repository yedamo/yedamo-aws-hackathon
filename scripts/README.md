# 배포 스크립트

## deploy.sh
프론트엔드 수동 배포를 위한 스크립트

### 사용법
```bash
# 프로젝트 루트에서 실행
./scripts/deploy.sh
```

### 실행 내용
1. frontend 폴더로 이동
2. 의존성 설치 (yarn install)
3. 빌드 실행 (yarn build)
4. S3 업로드
5. CloudFront 캐시 무효화

### 필요 조건
- AWS CLI 설정 (hackathon 프로필)
- yarn 설치
- 적절한 AWS 권한