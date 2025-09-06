# 예다모 : AI 사주 상담사

## 어플리케이션 개요

**AI 사주 상담사**는 전통 사주명리학과 AI 기술을 결합하여 개인 맞춤형 운세 상담을 제공하는 서비스입니다. 사용자의 생년월일, 출생시간 등 기본 정보와 구체적인 질문을 입력받아 사주팔자, 대운, 세운을 종합 분석하여 신뢰할 수 있는 조언을 제공합니다.

기존의 단순한 운세 서비스와 달리, 동양철학의 깊이 있는 이론을 바탕으로 하면서도 일반인이 쉽게 이해할 수 있도록 정제된 해석을 제공하는 것이 특징입니다. 복잡한 만세력 해석 과정을 AI가 대신 처리하여 누구나 쉽게 전문적인 사주 상담을 받을 수 있습니다.

## 주요 기능

### 1. 개인정보 입력 및 사주 계산
- 생년월일, 출생시간, 양력/음력, 성별, 이름 입력
- 자동 사주팔자 계산 및 대운/세운 분석
- 음양오행, 십신, 12운성 등 전문 데이터 활용

### 2. 대화형 질문 상담
- 구체적인 고민이나 질문 입력
- 사주 분석 결과와 연계한 맞춤형 조언 제공
- 추가 질문을 통한 심화 상담 가능

### 3. 종합 운세 분석
- **사주팔자**: 기본 성격과 타고난 운명 분석
- **대운**: 10년 단위 인생 흐름 예측
- **세운**: 올해와 내년의 운세 전망
- 월운 및 일운까지 세밀한 분석 제공

### 4. 이해하기 쉬운 해석
- 전문 용어를 일반인도 이해할 수 있게 설명
- 구체적이고 실용적인 조언 제공
- 복잡한 명리학 이론을 간단명료하게 정리

## 동영상 데모

Amazon Q Developer로 구현한 어플리케이션의 데모 영상을 입력합니다.
**Git의 Readme에는 GIF 형식으로 업로드하며, 원본 동영상은 발표 Presentation에 제출합니다.**

## 리소스 배포하기

### 아키텍처
```
사용자 → API Gateway → Lambda (Supervisor) → 멀티에이전트
                                          ├── SajuAgent (사주팔자 + MCP)
                                          ├── FortuneAgent (운세예측)  
                                          ├── CompatibilityAgent (궁합)
                                          ├── QuestionAnalyzer (질문분석)
                                          ├── ResponseGenerator (응답생성)
                                          └── KnowledgeAgent (RAG)
                                          ↓
                                      Amazon Bedrock
```

### 배포 방법

**1. 사전 요구사항**
- AWS CLI 설치 및 구성
- Python 3.11+
- AWS CDK 설치: `npm install -g aws-cdk`

**2. 배포 실행**
```bash
# 배포
python deploy.py

# 리소스 삭제
python deploy.py destroy
```

**3. 테스트**
```bash
# 테스트 클라이언트 실행
python test_client.py
```

### 배포되는 AWS 리소스
- **API Gateway**: REST API 엔드포인트
- **Lambda Function**: 멀티에이전트 Supervisor 시스템
  - SajuAgent: 사주팔자 계산 (MCP 지원)
  - FortuneAgent: 운세 예측 (대운/세운)
  - CompatibilityAgent: 궁합 분석
  - QuestionAnalyzer: 질문 분류 및 분석
  - ResponseGenerator: 통합 응답 생성
  - KnowledgeAgent: 명리학 지식베이스
- **IAM Role**: Lambda 실행 권한 (Bedrock 접근 포함)
- **CloudWatch Logs**: 로그 저장

### API 사용법

**기본 형식:**
```bash
curl -X POST https://your-api-url/saju \
  -H "Content-Type: application/json" \
  -d '{
    "birth_info": {
      "year": 1990,
      "month": 5,
      "day": 15,
      "hour": 14
    },
    "question": "올해 운세는 어떤가요?"
  }'
```

**MCP 지원 형식:**
```bash
curl -X POST https://your-api-url/saju \
  -H "Content-Type: application/json" \
  -d '{
    "birth_info": {
      "birth_date": "1990-05-15",
      "birth_time": "14:00",
      "calendar": "solar",
      "gender": "male"
    },
    "question": "내 사주팔자를 분석해주세요"
  }'
```

## 멀티에이전트 시스템 특징

### 지능형 라우팅
- **QuestionAnalyzer**: 사용자 질문을 자동 분류
- **Supervisor**: 적절한 전문 에이전트로 라우팅
- **통합 응답**: 여러 에이전트 결과를 종합

### MCP (Model Context Protocol) 지원
- **정밀 사주 계산**: @mymcp-fun/bazi 활용
- **폴백 메커니즘**: MCP 실패 시 기본 계산

### RAG 기반 지식베이스
- **KnowledgeAgent**: 명리학 전문 지식 활용
- **오행 상극**: 전통 이론 기반 해석

## 테스트 케이스

1. **사주팔자 분석**: "내 사주팔자를 분석해주세요"
2. **운세 예측**: "올해와 내년 운세는 어떤가요?"
3. **궁합 분석**: "연애운과 결혼 적기가 언제인가요?"
4. **직업 상담**: "이직을 고려 중인데 언제가 좋을까요?"
5. **건강 운세**: "건강에 주의할 점이 있나요?"

## 기대 효과

- **전문성**: 각 영역별 전문 에이전트로 정확한 상담
- **효율성**: 질문 자동 분류로 빠른 응답
- **확장성**: 새로운 에이전트 추가 용이
- **신뢰성**: MCP와 RAG로 정확한 명리학 이론 적용
