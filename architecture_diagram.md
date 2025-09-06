# 예다모 AI 사주 상담 서비스 - 현재 구현 아키텍처

## 전체 시스템 아키텍처

```mermaid
graph TB
    %% 사용자 레이어
    User[👤 사용자] --> API[🌐 API Gateway]
    
    %% API Gateway
    API --> |POST /saju| Lambda[⚡ Lambda Function]
    
    %% Lambda 내부 구조
    subgraph "Lambda Function (Python 3.11)"
        Handler[📥 index.py handler] --> Supervisor[🎯 SupervisorAgent]
        
        %% 멀티에이전트 시스템
        subgraph "멀티에이전트 시스템"
            Supervisor --> QA[🔍 QuestionAnalyzer]
            Supervisor --> SA[📊 SajuAgent]
            Supervisor --> FA[🔮 FortuneAgent]
            Supervisor --> CA[💕 CompatibilityAgent]
            Supervisor --> RG[📝 ResponseGenerator]
            Supervisor --> KA[📚 KnowledgeAgent]
        end
        
        %% MCP 지원
        SA --> |MCP 호출| MCP[🔧 @mymcp-fun/bazi]
        SA --> |폴백| BasicCalc[⚙️ 기본 사주 계산]
    end
    
    %% 외부 서비스
    Lambda --> Bedrock[🤖 Amazon Bedrock<br/>Claude-3-Haiku]
    
    %% AWS 인프라
    subgraph "AWS 인프라"
        IAM[🔐 IAM Role<br/>Bedrock 권한]
        CW[📊 CloudWatch Logs]
        Lambda -.-> IAM
        Lambda -.-> CW
    end
    
    %% 응답 흐름
    Lambda --> |JSON Response| API
    API --> User
    
    %% 스타일링
    classDef userClass fill:#e1f5fe
    classDef awsClass fill:#fff3e0
    classDef agentClass fill:#f3e5f5
    classDef mcpClass fill:#e8f5e8
    
    class User userClass
    class API,Lambda,Bedrock,IAM,CW awsClass
    class QA,SA,FA,CA,RG,KA agentClass
    class MCP,BasicCalc mcpClass
```

## 멀티에이전트 시스템 상세 구조

```mermaid
graph LR
    %% 입력
    Input[📥 사용자 입력<br/>birth_info + question] --> Supervisor[🎯 Supervisor Agent]
    
    %% 1단계: 질문 분석
    Supervisor --> QA[🔍 Question Analyzer]
    QA --> |분석 결과| Supervisor
    
    %% 2단계: 사주 데이터 생성
    Supervisor --> SA[📊 Saju Agent]
    SA --> MCP{🔧 MCP 지원?}
    MCP -->|Yes| MCPCall[📞 @mymcp-fun/bazi]
    MCP -->|No/Fail| Basic[⚙️ 기본 계산]
    MCPCall --> SajuData[📋 사주 데이터]
    Basic --> SajuData
    
    %% 3단계: RAG 지식베이스
    Supervisor --> KA[📚 Knowledge Agent]
    KA --> RAG[🧠 명리학 지식베이스]
    
    %% 4단계: 전문 에이전트 라우팅
    Supervisor --> Router{🎯 에이전트 라우팅}
    Router -->|사주팔자| SA
    Router -->|운세예측| FA[🔮 Fortune Agent]
    Router -->|궁합분석| CA[💕 Compatibility Agent]
    
    %% 5단계: 응답 생성
    SA --> RG[📝 Response Generator]
    FA --> RG
    CA --> RG
    KA --> RG
    
    %% 최종 출력
    RG --> Output[📤 통합 응답<br/>JSON Format]
    
    %% 스타일링
    classDef inputClass fill:#e3f2fd
    classDef processClass fill:#f3e5f5
    classDef outputClass fill:#e8f5e8
    classDef decisionClass fill:#fff3e0
    
    class Input,Output inputClass
    class Supervisor,QA,SA,FA,CA,RG,KA,MCPCall,Basic,RAG processClass
    class MCP,Router decisionClass
```

## 데이터 흐름 다이어그램

```mermaid
sequenceDiagram
    participant U as 👤 사용자
    participant API as 🌐 API Gateway
    participant L as ⚡ Lambda
    participant S as 🎯 Supervisor
    participant QA as 🔍 QuestionAnalyzer
    participant SA as 📊 SajuAgent
    participant MCP as 🔧 MCP Server
    participant KA as 📚 KnowledgeAgent
    participant RG as 📝 ResponseGenerator
    participant B as 🤖 Bedrock
    
    U->>API: POST /saju {birth_info, question}
    API->>L: Lambda 호출
    L->>S: route_request()
    
    %% 1단계: 질문 분석
    S->>QA: analyze(question)
    QA->>B: 질문 분류 요청
    B-->>QA: 분석 결과
    QA-->>S: {category, urgency}
    
    %% 2단계: 사주 데이터 생성
    S->>SA: get_bazi_info(birth_info)
    alt MCP 지원 가능
        SA->>MCP: npx @mymcp-fun/bazi
        MCP-->>SA: 정밀 사주 데이터
    else MCP 실패/미지원
        SA->>SA: calculate_saju_basic()
        SA-->>SA: 기본 사주 데이터
    end
    SA-->>S: bazi_data
    
    %% 3단계: RAG 지식베이스
    S->>KA: get_bazi_interpretation()
    KA->>KA: 명리학 지식 검색
    KA-->>S: knowledge_interpretation
    
    %% 4단계: 전문 에이전트 처리
    S->>S: _classify_request()
    alt 사주팔자 질문
        S->>SA: process()
        SA->>B: 사주 분석 요청
        B-->>SA: 분석 결과
    else 운세 질문
        S->>FA: process()
        FA->>B: 운세 분석 요청
        B-->>FA: 분석 결과
    else 궁합 질문
        S->>CA: process()
        CA->>B: 궁합 분석 요청
        B-->>CA: 분석 결과
    end
    
    %% 5단계: 응답 통합
    S->>S: _enhance_with_knowledge()
    S->>RG: generate_response()
    RG->>B: 통합 응답 생성
    B-->>RG: 최종 응답
    RG-->>S: enhanced_result
    
    S-->>L: 통합 응답
    L-->>API: JSON Response
    API-->>U: 사주 상담 결과
```

## AWS 리소스 구성

```mermaid
graph TB
    subgraph "AWS Account"
        subgraph "API Gateway"
            REST[REST API<br/>yedamo-saju-service]
            Resource[/saju Resource]
            Method[POST Method]
            REST --> Resource
            Resource --> Method
        end
        
        subgraph "Lambda"
            Function[Lambda Function<br/>Python 3.11<br/>512MB, 60s timeout]
            Code[Code Package<br/>- index.py<br/>- supervisor.py<br/>- agents/]
            Env[Environment Variables<br/>MODEL_ID<br/>SUPERVISOR_ENABLED]
            Function --> Code
            Function --> Env
        end
        
        subgraph "IAM"
            Role[Lambda Execution Role]
            BasicPolicy[AWSLambdaBasicExecutionRole]
            BedrockPolicy[Bedrock InvokeModel Policy]
            Role --> BasicPolicy
            Role --> BedrockPolicy
        end
        
        subgraph "Bedrock"
            Claude[Claude-3-Haiku<br/>anthropic.claude-3-haiku-20240307-v1:0]
        end
        
        subgraph "CloudWatch"
            Logs[Lambda Logs<br/>/aws/lambda/function-name]
        end
        
        Method --> Function
        Function --> Role
        Function --> Claude
        Function --> Logs
    end
    
    %% 외부 연결
    Internet[🌐 Internet] --> REST
    MCP_External[📦 NPM Registry<br/>@mymcp-fun/bazi] -.-> Function
    
    %% 스타일링
    classDef awsService fill:#ff9800,color:#fff
    classDef compute fill:#4caf50,color:#fff
    classDef storage fill:#2196f3,color:#fff
    classDef security fill:#f44336,color:#fff
    classDef external fill:#9e9e9e,color:#fff
    
    class REST,Resource,Method,Claude,Logs awsService
    class Function,Code,Env compute
    class Role,BasicPolicy,BedrockPolicy security
    class Internet,MCP_External external
```

## 에이전트별 역할 및 특징

| 에이전트 | 역할 | 주요 기능 | 특징 |
|---------|------|-----------|------|
| **SupervisorAgent** | 🎯 총괄 관리자 | - 요청 라우팅<br/>- 에이전트 조율<br/>- 응답 통합 | - 지능형 라우팅<br/>- 폴백 메커니즘<br/>- RAG 통합 |
| **QuestionAnalyzer** | 🔍 질문 분석가 | - 질문 분류<br/>- 긴급도 판단<br/>- 의도 파악 | - Bedrock 기반 분석<br/>- 카테고리 분류 |
| **SajuAgent** | 📊 사주 전문가 | - 사주팔자 계산<br/>- MCP 연동<br/>- 기본 성격 분석 | - MCP 우선 사용<br/>- 폴백 지원<br/>- 정밀 계산 |
| **FortuneAgent** | 🔮 운세 예측가 | - 대운/세운 분석<br/>- 월운/일운 예측<br/>- 시기별 조언 | - 시간대별 분석<br/>- 구체적 예측 |
| **CompatibilityAgent** | 💕 궁합 분석가 | - 인간관계 분석<br/>- 연애/결혼 궁합<br/>- 상성 진단 | - 관계 중심 분석<br/>- 실용적 조언 |
| **ResponseGenerator** | 📝 응답 생성기 | - 통합 응답 생성<br/>- 자연어 처리<br/>- 형식 표준화 | - 일관된 형식<br/>- 이해하기 쉬운 설명 |
| **KnowledgeAgent** | 📚 지식 관리자 | - RAG 지식베이스<br/>- 명리학 이론<br/>- 전문 해석 | - 전통 이론 기반<br/>- 신뢰성 높은 해석 |

## 기술 스택 및 특징

### 🛠️ 기술 스택
- **Backend**: Python 3.11, AWS Lambda
- **AI/ML**: Amazon Bedrock (Claude-3-Haiku)
- **API**: AWS API Gateway (REST)
- **Infrastructure**: AWS CDK
- **MCP**: @mymcp-fun/bazi (Node.js)
- **Monitoring**: CloudWatch Logs

### ⭐ 주요 특징
1. **멀티에이전트 아키텍처**: 전문 영역별 에이전트 분리
2. **지능형 라우팅**: 질문 분석 기반 적절한 에이전트 선택
3. **MCP 지원**: 정밀한 사주 계산을 위한 외부 패키지 연동
4. **폴백 메커니즘**: MCP 실패 시 기본 계산으로 대체
5. **RAG 통합**: 명리학 전문 지식베이스 활용
6. **서버리스**: AWS Lambda 기반 확장 가능한 구조
7. **CORS 지원**: 웹 프론트엔드 연동 준비

### 🔄 처리 흐름
1. **요청 수신** → API Gateway
2. **질문 분석** → QuestionAnalyzer
3. **사주 계산** → SajuAgent (MCP/폴백)
4. **전문 분석** → 해당 에이전트
5. **지식 보강** → KnowledgeAgent (RAG)
6. **응답 통합** → ResponseGenerator
7. **결과 반환** → JSON 형식

이 아키텍처는 확장 가능하고 유지보수가 용이하며, 각 에이전트의 독립적인 개발과 테스트를 지원합니다.