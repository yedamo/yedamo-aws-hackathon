# Independent Saju Image Generation Service

## 개요
메인 yedamo 스택과 완전히 분리된 독립적인 이미지 생성 서비스입니다.

## 파일 구조
```
backend/image-service/
├── independent-image-service.yaml  # CloudFormation 템플릿
├── deploy-independent-image.sh     # 배포 스크립트
├── test-api.py                     # API 테스트 스크립트
└── README.md                       # 이 문서
```

## 배포 방법

### 1. 독립 스택 배포
```bash
cd backend/image-service
./deploy-independent-image.sh
```

### 2. API URL 확인
배포 완료 후 출력되는 API URL을 복사합니다.

### 3. 환경 변수 설정
`frontend/.env` 파일에서 `VITE_IMAGE_API_URL`을 실제 API URL로 업데이트:
```
VITE_IMAGE_API_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/generate
```

### 4. API 테스트
```bash
# 기본 테스트
./test-api.py https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/generate

# 이미지 저장하며 테스트
./test-api.py https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/generate --save
```

## 스택 구성
- **스택명**: `saju-independent-image-service`
- **Lambda 함수**: `saju-independent-image-generator`
- **API Gateway**: `saju-independent-image-api`
- **IAM 역할**: `saju-independent-image-generator-role`

## 장점
- ✅ 메인 스택과 완전 분리
- ✅ 다른 개발자 작업에 영향받지 않음
- ✅ 독립적인 배포 및 관리
- ✅ 롤백 위험 없음

## API 엔드포인트
```
POST /generate
```

### 요청 예시
```json
{
  "animal": "용",
  "color": "금색",
  "gender": "male",
  "elements": {
    "wood": 1,
    "fire": 2,
    "earth": 1,
    "metal": 3,
    "water": 1
  },
  "dominant_element": "metal",
  "yin_yang_balance": "yang_dominant"
}
```

### 응답 예시
```json
{
  "success": true,
  "image": "base64_encoded_image_data",
  "prompt": "generated_prompt",
  "color": "금색",
  "animal": "용",
  "gender": "male",
  "dominant_element": "metal",
  "yin_yang_balance": "yang_dominant"
}
```

## 스택 삭제
```bash
aws cloudformation delete-stack --stack-name saju-independent-image-service
```
