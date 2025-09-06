# Bedrock Nova Canvas 이미지 생성 서비스 배포 완료

## 🎉 배포 성공!

AWS CDK와 CloudFormation을 사용하여 Bedrock Nova Canvas 모델을 활용한 이미지 생성 API가 성공적으로 배포되었습니다.

## 📋 서비스 정보

### API 엔드포인트
- **URL**: `https://05r6l272gj.execute-api.us-east-1.amazonaws.com/prod/image`
- **Method**: POST
- **Content-Type**: application/json

### 요청 형식
```json
{
  "color": "빨간",
  "animal": "용"
}
```

### 지원되는 12지신 동물
- 쥐, 소, 호랑이, 토끼, 용, 뱀, 말, 양, 원숭이, 닭, 개, 돼지

## 🏗️ 인프라 구성

### AWS 리소스
1. **Lambda Function**: `yedamo-image-generator`
   - Runtime: Python 3.11
   - Memory: 1024 MB
   - Timeout: 120초
   - Handler: `image_generator.lambda_handler`

2. **API Gateway**: REST API
   - Stage: prod
   - CORS 활성화
   - Lambda Proxy Integration

3. **IAM Role**: `yedamo-image-generator-role`
   - Bedrock InvokeModel 권한
   - Lambda 기본 실행 권한

### 사용된 AI 모델
- **Amazon Nova Canvas** (`amazon.nova-canvas-v1:0`)
- 텍스트-이미지 생성 모델
- 1024x1024 해상도 지원

## 🧪 테스트 결과

### 성공적으로 생성된 이미지
1. `generated_빨간_용_20250906_114415.png` (2.0MB)
2. `generated_파란_호랑이_20250906_114424.png` (2.0MB)
3. `generated_금색_닭_20250906_114434.png` (2.1MB)

### 테스트 명령어
```bash
curl -X POST https://05r6l272gj.execute-api.us-east-1.amazonaws.com/prod/image \
  -H 'Content-Type: application/json' \
  -d '{"color": "빨간", "animal": "용"}'
```

## 📁 프로젝트 구조

```
yedamo-aws-hackathon/
├── lambda/
│   ├── image_generator.py          # Lambda 함수 코드
│   ├── requirements_image.txt      # Python 의존성
│   └── lambda-deployment.zip       # 배포 패키지
├── cloudformation/
│   ├── image-generator.yaml        # 원본 CloudFormation 템플릿
│   └── simple-image-generator.yaml # 단순화된 템플릿
├── cdk/                            # CDK 프로젝트 (기존)
├── deploy-direct.sh                # 직접 배포 스크립트
├── test_image_api.py              # API 테스트 스크립트
└── generated_*.png                # 생성된 이미지 파일들
```

## 🔧 주요 기능

1. **색상 + 12지신 동물** 조합으로 이미지 생성
2. **한국 전통 예술 스타일** 적용
3. **Base64 형식**으로 이미지 반환
4. **CORS 지원**으로 웹 애플리케이션 연동 가능
5. **입력 검증** 및 **에러 처리**

## 🚀 사용 방법

### Python 예제
```python
import requests
import base64

url = "https://05r6l272gj.execute-api.us-east-1.amazonaws.com/prod/image"
data = {"color": "빨간", "animal": "용"}

response = requests.post(url, json=data)
result = response.json()

if result.get('success'):
    # Base64 이미지 데이터를 파일로 저장
    image_data = base64.b64decode(result['image'])
    with open('generated_image.png', 'wb') as f:
        f.write(image_data)
```

### JavaScript 예제
```javascript
fetch('https://05r6l272gj.execute-api.us-east-1.amazonaws.com/prod/image', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        color: '빨간',
        animal: '용'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Base64 이미지를 img 태그에 표시
        const img = document.createElement('img');
        img.src = 'data:image/png;base64,' + data.image;
        document.body.appendChild(img);
    }
});
```

## 💰 비용 고려사항

- **Lambda 실행**: 요청당 약 2초 실행 (1024MB 메모리)
- **Bedrock Nova Canvas**: 이미지 생성당 과금
- **API Gateway**: 요청당 과금
- **데이터 전송**: 이미지 크기(~2MB)에 따른 전송 비용

## 🔒 보안 고려사항

- API는 현재 인증 없이 공개 접근 가능
- 프로덕션 환경에서는 API Key 또는 인증 추가 권장
- Rate limiting 설정 고려

## 📞 문의 및 지원

이 서비스는 AWS Bedrock Nova Canvas를 활용한 데모 프로젝트입니다.
추가 기능이나 개선사항이 필요하시면 언제든 문의해 주세요!
