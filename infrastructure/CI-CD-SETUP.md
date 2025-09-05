# CI/CD 파이프라인 설정 가이드

## 개요
GitHub 리포지토리와 AWS CodeBuild를 연결하여 frontend 폴더 변경시에만 자동 배포되는 파이프라인을 구축합니다.

## 1. CodeBuild 프로젝트 생성 완료
✅ **yedamo-frontend-build** 프로젝트가 생성되었습니다.

## 2. GitHub 연결 설정 (수동)

### AWS 콘솔에서 설정
1. **AWS CodeBuild 콘솔** 접속
2. **yedamo-frontend-build** 프로젝트 선택
3. **소스** 탭에서 **편집** 클릭
4. **GitHub** 선택 후 **OAuth로 연결** 클릭
5. GitHub 계정 인증 완료

### 웹훅 설정
1. CodeBuild 프로젝트 상세 페이지
2. **웹훅** 섹션에서 **웹훅 생성** 클릭
3. 이벤트 유형: **PUSH**
4. 브랜치 필터: **HEAD_REF** = `^refs/heads/main$`

## 3. 스마트 배포 플로우

```
GitHub Push → 변경사항 감지 → frontend 폴더 변경시만 → 빌드 실행 → S3 업로드 → CloudFront 무효화
```

### 변경사항 감지 로직
- **frontend/** 폴더 변경시: 빌드 및 배포 실행
- **다른 폴더 변경시**: 빌드 스킵, 리소스 절약

### buildspec.yml 주요 기능
```yaml
pre_build:
  - git diff로 변경된 파일 확인
  - frontend/ 폴더 변경사항 감지
  - SHOULD_BUILD 환경변수 설정

install/build/post_build:
  - SHOULD_BUILD=true일 때만 실행
  - 불필요한 빌드 방지로 비용 절약
```

## 4. 테스트 방법

### frontend 변경시 (빌드 실행)
```bash
# frontend 파일 수정 후
git add frontend/
git commit -m "Update frontend"
git push origin main
# → CodeBuild 실행됨
```

### 다른 폴더 변경시 (빌드 스킵)
```bash
# backend 파일 수정 후
git add backend/
git commit -m "Update backend"
git push origin main
# → CodeBuild 실행되지만 빌드 스킵
```

### 수동 빌드 실행
```bash
aws codebuild start-build --project-name yedamo-frontend-build --profile hackathon
```

## 5. 리소스 정보

- **CodeBuild 프로젝트**: `yedamo-frontend-build`
- **S3 버킷**: `yedamo-frontend-3si02day`
- **CloudFront ID**: `E1LD293UU79DMN`
- **웹사이트 URL**: https://do6x992wzv6m5.cloudfront.net

## 6. 비용 최적화

### 스마트 빌드로 절약
- **frontend 변경시만 빌드**: 불필요한 빌드 방지
- **빌드 시간**: 2-3분 (변경시에만)
- **월 예상 비용**: 실제 변경 횟수에 따라 대폭 절약

### 빌드 로그 예시
```
Frontend changes detected. Proceeding with build...
# 또는
No frontend changes detected. Skipping build...
```

## 7. 문제 해결

### 변경사항 감지 실패시
1. git history 확인
2. HEAD~1 비교 로직 검증
3. 수동 빌드로 우회

### GitHub 연결 문제
1. OAuth 토큰 재생성
2. 리포지토리 권한 확인
3. 웹훅 설정 재확인