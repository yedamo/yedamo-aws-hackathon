# 예다모 API 문서

## 개요
예다모는 AI 사주 상담사 서비스로, 사주팔자 분석과 이미지 생성 기능을 제공합니다.

## 기본 정보
- **Base URL**: `https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod`
- **Content-Type**: `application/json`
- **CORS**: 모든 도메인 허용
- **Timeout**: 30초 (일반 API), 180초 (이미지 생성)

## API 엔드포인트

### 1. 기본 사주 분석 API

#### `POST /saju/basic`
사용자의 생년월일 정보를 바탕으로 기본 사주 정보를 반환합니다.

**요청 형식 1 (이름 포함):**
```json
{
  "name": "김다롬",
  "birth_info": {
    "year": 1997,
    "month": 5,
    "day": 19,
    "hour": 12,
    "gender": "female",
    "region": "korea"
  }
}
```
"region": ["korea", "usa_east", "usa_west", "china", "japan"]

**요청 형식 2 (기본):**
```json
{
  "birth_info": {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "gender": "male",
    "timezone": "Asia/Shanghai"
  }
}
```

**응답 예시:**
```json
{
  "success": true,
  "cache_key": "1234567890_김다롬",
  "saju_analysis": {
    "basic_info": "사주팔자 기본 정보",
    "personality": "성격 분석",
    "fortune": "운세 정보",
    "wuxing": "오행 분석"
  },
  "birth_info": {
    "year": 1997,
    "month": 5,
    "day": 19,
    "hour": 12,
    "gender": "female"
  }
}
```

### 2. 사주 상담 API

#### `POST /saju/consultation`
구체적인 질문에 대한 사주 상담을 제공합니다.

**요청 형식 1 (캐시 키 사용):**
```json
{
  "cache_key": "1234567890_김다롬",
  "question": "올해 운세는 어떤가요?"
}
```

**요청 형식 2 (직접 생년월일):**
```json
{
  "birth_info": {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "gender": "male"
  },
  "question": "올해 운세와 직장운이 어떤가요?"
}
```

**응답 예시:**
```json
{
  "success": true,
  "agent_type": "FortuneAgent",
  "consultation": "상세한 사주 상담 내용...",
  "question": "올해 운세는 어떤가요?",
  "analysis_type": "fortune_prediction"
}
```

### 3. 이미지 생성 API

#### `POST /image`
12지신 동물과 색상을 기반으로 AI 이미지를 생성합니다.

**요청 예시:**
```json
{
  "color": "빨간",
  "animal": "용"
}
```

**응답 예시:**
```json
{
  "success": true,
  "prompt": "빨간 용의 이미지",
  "color": "빨간",
  "animal": "용",
  "image": "base64_encoded_image_data"
}
```

**지원되는 동물:**
- 12지신: 쥐, 소, 호랑이, 토끼, 용, 뱀, 말, 양, 원숭이, 닭, 개, 돼지

## 요청 파라미터 상세

### birth_info 객체
| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| year | integer | ✅ | 출생년도 | 1990 |
| month | integer | ✅ | 출생월 (1-12) | 5 |
| day | integer | ✅ | 출생일 (1-31) | 15 |
| hour | integer | ✅ | 출생시간 (0-23) | 14 |
| gender | string | ✅ | 성별 ("male", "female") | "male" |
| timezone | string | ❌ | 시간대 | "Asia/Shanghai" |
| region | string | ❌ | 지역 | "korea" |

### 추가 파라미터
| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| name | string | ❌ | 이름 (캐시 키 생성용) | "김다롬" |
| cache_key | string | ❌ | 기존 캐시 키 | "1234567890_김다롬" |
| question | string | ✅ | 상담 질문 | "올해 운세는 어떤가요?" |
| color | string | ✅ | 이미지 색상 | "빨간" |
| animal | string | ✅ | 12지신 동물 | "용" |

## 멀티에이전트 시스템

### 에이전트 종류
1. **SajuAgent**: 사주팔자 계산 (MCP 지원)
2. **FortuneAgent**: 운세 예측 (대운/세운)
3. **CompatibilityAgent**: 궁합 분석
4. **QuestionAnalyzer**: 질문 분류 및 분석
5. **ResponseGenerator**: 통합 응답 생성
6. **KnowledgeAgent**: 명리학 지식베이스 (RAG)

### 질문 유형별 라우팅
- **사주팔자 분석**: "내 사주팔자를 분석해주세요" → SajuAgent
- **운세 예측**: "올해 운세는 어떤가요?" → FortuneAgent
- **궁합 분석**: "연애운은 어떤가요?" → CompatibilityAgent
- **일반 상담**: 기타 질문 → 적절한 에이전트 조합

## 오류 처리

### 공통 오류 응답
```json
{
  "success": false,
  "error": "오류 메시지",
  "code": "ERROR_CODE"
}
```

### 주요 오류 코드
- `400`: 잘못된 요청 (필수 파라미터 누락)
- `404`: 경로를 찾을 수 없음
- `500`: 서버 내부 오류
- `TIMEOUT`: 요청 시간 초과 (이미지 생성 시 3분)

## 캐싱 시스템

### Redis 캐싱
- **사주 분석 결과**: 동일한 생년월일 정보에 대해 캐싱
- **이미지 생성**: 동일한 색상/동물 조합에 대해 캐싱
- **TTL**: 30분 (사주 캐시), 24시간 (이미지 캐시)
- **갱신 임계값**: 5분 (캐시 만료 5분 전 자동 갱신)

### 캐시 키 형식
- 사주: `{timestamp}_{name}` (예: `1234567890_김다롬`)
- 이미지: `image:{color}_{animal}`

### 캐시 기반 워크플로우
1. **1단계**: `/saju/basic` 호출로 사주 계산 및 캐시 생성
2. **2단계**: 반환된 `cache_key`로 `/saju/consultation` 반복 호출
3. **장점**: 동일한 생년월일 재계산 없이 빠른 질의응답

## 보안 및 제한사항

### 요청 제한
- **타임아웃**: 이미지 생성 API는 최대 3분
- **페이로드 크기**: 최대 1MB
- **동시 요청**: 제한 없음 (AWS Lambda 동시성 제한 적용)

### 데이터 보호
- 개인정보는 캐시에만 임시 저장
- 로그에는 민감정보 제외
- HTTPS 통신 필수

## 테스트 방법

### cURL 예시
```bash
# 기본 사주 분석
curl -X POST https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod/saju/basic \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김다롬",
    "birth_info": {
      "year": 1997,
      "month": 5,
      "day": 19,
      "hour": 12,
      "gender": "female",
      "region": "korea"
    }
  }'

# 캐시 키를 사용한 상담
curl -X POST https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod/saju/consultation \
  -H "Content-Type: application/json" \
  -d '{
    "cache_key": "1234567890_김다롬",
    "question": "올해 운세는 어떤가요?"
  }'

# 이미지 생성
curl -X POST https://w3qvjjo80g.execute-api.us-east-1.amazonaws.com/prod/image \
  -H "Content-Type: application/json" \
  -d '{
    "color": "빨간",
    "animal": "용"
  }'
```

### Python 테스트 스크립트

#### 1. 기본 API 테스트
```bash
python test/test_client_new.py
```

#### 2. 캐시 기반 플로우 테스트
```bash
python test/test_client_cached.py
```

#### 3. 이미지 생성 테스트
```bash
python test_image_api.py
```

### 테스트 시나리오

#### 캐시 기반 워크플로우
1. **기본 사주 조회**: 생년월일로 사주 계산 → `cache_key` 획득
2. **연속 질의응답**: `cache_key`로 다양한 질문 상담
3. **캐시 만료 테스트**: 잘못된 캐시 키로 오류 확인

#### 질문 유형별 테스트
- "올해 운세는 어떤가요?" → FortuneAgent
- "직장운과 재물운이 궁금합니다." → FortuneAgent
- "연애운은 어떤가요?" → CompatibilityAgent

## 배포 정보

### AWS 리소스
- **API Gateway**: REST API 엔드포인트
- **Lambda Function**: 멀티에이전트 시스템
- **Redis**: 캐싱 (ElastiCache 또는 로컬)
- **Bedrock**: AI 모델 (Claude, Titan 등)

### 환경 변수
- `BACKEND_URL`: 백엔드 서버 URL
- `REDIS_HOST`: Redis 호스트
- `REDIS_PORT`: Redis 포트
- `AWS_REGION`: AWS 리전

## 업데이트 로그

### v1.0.0 (2025-09-06)
- 기본 사주 분석 API 구현
- 사주 상담 API 구현
- 이미지 생성 API 구현
- 멀티에이전트 시스템 구축
- Redis 캐싱 시스템 구현
