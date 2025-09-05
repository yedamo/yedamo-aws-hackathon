Amazon Q can now help you write, modify, and maintain code by combining the power of natural language understanding with the ability to take actions on your behalf such as directly making code changes, modifying files, and running commands.

---

<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 200px 0 20px 0;">

<div style="font-size: 24px; margin-bottom: 12px;"><strong>Amazon Q</strong></div>
<div style="background: rgba(128, 128, 128, 0.15); border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px; padding: 8px; margin: 4px 0; text-align: center;">
<div style="font-size: 14px; margin-bottom: 4px;"><strong>Did you know?</strong></div>
<div>MCP is available in Amazon Q!</div>
</div>

Select code & ask me to explain, debug or optimize it, or type `/` for quick actions

</div>

---

현재 구현된 아키텍처 diagram 그려줘

---

현재 프로젝트의 구조를 파악하기 위해 먼저 디렉토리를 살펴보겠습니다.

---

이제 주요 구성 요소들을 확인해보겠습니다.

---

이제 에이전트들의 구조도 확인해보겠습니다.

---

이제 현재 구현된 아키텍처 다이어그램을 생성하겠습니다.

---

현재 구현된 예다모 사주 상담 서비스의 아키텍처 다이어그램을 생성합니다.

---


현재 구현된 예다모 AI 사주 상담 서비스의 아키텍처 다이어그램을 생성했습니다. 

주요 특징:

## 🏗️ 전체 아키텍처
- **서버리스**: API Gateway + Lambda 기반
- **멀티에이전트**: 7개 전문 에이전트로 구성
- **AI 통합**: Amazon Bedrock Claude-3-Haiku 활용

## 🤖 멀티에이전트 시스템
1. **SupervisorAgent**: 총괄 관리 및 라우팅
2. **QuestionAnalyzer**: 지능형 질문 분석
3. **SajuAgent**: MCP 지원 사주팔자 계산
4. **FortuneAgent**: 운세 예측 전문
5. **CompatibilityAgent**: 궁합 분석 전문
6. **ResponseGenerator**: 통합 응답 생성
7. **KnowledgeAgent**: RAG 기반 명리학 지식

## 🔧 핵심 기능
- **MCP 연동**: @mymcp-fun/bazi로 정밀 사주 계산
- **폴백 메커니즘**: MCP 실패 시 기본 계산
- **RAG 지원**: 전통 명리학 지식베이스 활용
- **지능형 라우팅**: 질문 분석 기반 에이전트 선택

다이어그램은 `architecture_diagram.md` 파일에 저장되었으며, Mermaid 형식으로 작성되어 GitHub나 지원하는 마크다운 뷰어에서 시각적으로 확인할 수 있습니다.

---

agent 가 bedrock 사용했다고 하는데 왜 콘솔에서 bedrock 탭에서 안보여? 그냥 lambda 에서 API 만으로도 사용할 수 있는거야?

---

네, 맞습니다! Lambda에서 Bedrock API만으로 사용할 수 있습니다. Bedrock 콘솔에서 안 보이는 이유를 설명드리겠습니다.

## 🔍 Bedrock 사용 방식

### 1. **API 호출 방식** (현재 구현)
```python
# lambda/agents/base_agent.py에서
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({...})
)
```

### 2. **콘솔에서 안 보이는 이유**
- **API 직접 호출**: 콘솔 UI 없이 프로그래밍 방식으로만 사용
- **런타임 호출**: `bedrock-runtime` 서비스로 모델 추론만 실행
- **관리형 서비스**: 별도 리소스 생성 없이 AWS 관리 모델 사용

## 📊 확인 방법

### CloudWatch에서 확인:

---

Bedrock 사용량과 로그를 확인하는 스크립트를 생성합니다.

---


## 🎯 핵심 포인트

### **Bedrock은 관리형 서비스**
- 별도 인스턴스나 리소스 생성 불필요
- API 호출만으로 즉시 사용 가능
- AWS가 모델 인프라 완전 관리

### **콘솔에서 확인할 수 있는 것들:**
1. **Bedrock 콘솔** → Model access → 모델 활성화 상태
2. **CloudWatch** → Lambda 로그에서 bedrock 호출 확인
3. **AWS Cost Explorer** → Bedrock 사용 비용

### **현재 구현의 장점:**
- **서버리스**: 인프라 관리 불필요
- **즉시 사용**: API 호출만으로 AI 기능 활용
- **비용 효율**: 사용한 만큼만 과금
- **확장성**: 자동 스케일링

실제로 Lambda에서 `boto3.client('bedrock-runtime')`로 호출하면 AWS가 관리하는 Claude 모델을 바로 사용할 수 있습니다. 콘솔에 별도 리소스가 안 보이는 게 정상입니다!

---

bedrock 의 agent 로 띄우는 게 아니라 API 를 사용해서 단순 모델을 call 하는게 응답 품질이 더 좋을까?

---

좋은 질문입니다! 현재 구현이 더 나은 선택입니다. 비교해보겠습니다:

## 🔄 현재 구현 (API 직접 호출) vs Bedrock Agent

### **현재 구현의 장점** ✅

```python
# 현재 방식: 직접 제어
bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    })
)
```

**1. 응답 품질**
- ✅ **정밀한 프롬프트 제어**: 사주 전문 프롬프트 최적화
- ✅ **컨텍스트 완전 제어**: 멀티에이전트 간 데이터 공유
- ✅ **도메인 특화**: 명리학 전문 용어와 로직 직접 구현

**2. 성능 & 비용**
- ✅ **빠른 응답**: 중간 레이어 없음
- ✅ **저렴한 비용**: Agent 추가 비용 없음
- ✅ **예측 가능한 비용**: 토큰 기반 과금만

**3. 개발 유연성**
- ✅ **완전한 제어**: 로직 자유롭게 구현
- ✅ **디버깅 용이**: 모든 단계 추적 가능
- ✅ **빠른 반복**: 즉시 수정/배포

### **Bedrock Agent의 한계** ❌

```python
# Bedrock Agent 방식
bedrock_agent.invoke_agent(
    agentId='AGENT_ID',
    agentAliasId='ALIAS_ID',
    inputText=user_input
)
```

**1. 응답 품질 이슈**
- ❌ **일반적 응답**: 사주 전문성 부족
- ❌ **제한된 커스터마이징**: 프롬프트 세밀 조정 어려움
- ❌ **컨텍스트 손실**: 멀티에이전트 간 데이터 연계 복잡

**2. 복잡성 증가**
- ❌ **추가 설정**: Agent, Knowledge Base, Action Group 구성
- ❌ **높은 비용**: Agent 실행 비용 + 모델 비용
- ❌ **느린 응답**: 여러 레이어 거쳐야 함

## 📊 실제 비교 예시

---

Bedrock API 직접 호출과 Agent 방식을 비교하는 스크립트를 생성합니다.

---


## 🎯 **결론: 현재 구현이 최적**

### **사주 상담 서비스 특성상**

1. **도메인 전문성 필요**
   - 명리학 전문 용어와 해석
   - 복잡한 사주 계산 로직
   - 개인화된 상담 스타일

2. **실시간 응답 중요**
   - 사용자 대화형 상담
   - 빠른 피드백 필요

3. **비용 효율성**
   - 스타트업/개인 프로젝트
   - 예측 가능한 비용 구조

### **언제 Bedrock Agent를 고려할까?**

- **일반적인 챗봇**: FAQ, 고객 서비스
- **문서 기반 QA**: 대량 문서 검색
- **복잡한 워크플로우**: 여러 외부 API 연동

### **현재 구현의 우수성**

```python
# 멀티에이전트 + 직접 API = 최고의 조합
class SupervisorAgent:
    def route_request(self, birth_info, question):
        # 1. 지능형 라우팅
        # 2. MCP 연동  
        # 3. RAG 지식베이스
        # 4. 전문 에이전트 처리
        # 5. 통합 응답 생성
```

**현재 구현이 Bedrock Agent보다 응답 품질과 성능 모두에서 우수합니다!** 🏆

---

bedrock agent 는 커스텀에 한계가 있어?

---

네, Bedrock Agent는 커스텀에 상당한 한계가 있습니다. 구체적으로 비교해보겠습니다:

## 🚫 Bedrock Agent의 커스텀 한계

### **1. 프롬프트 제어 한계**
```json
// Bedrock Agent - 제한적 프롬프트
{
  "instruction": "You are a fortune teller assistant...",
  // 단순한 instruction만 가능
  // 복잡한 프롬프트 엔지니어링 불가
}
```

```python
# 현재 구현 - 완전한 프롬프트 제어
prompt = f"""
당신은 사주명리학 전문가입니다.
다음 규칙을 엄격히 따라주세요:

1. 사주팔자 분석 순서:
   - 일간 {day_master} 분석
   - 월령 {month_season} 고려
   - 용신 {useful_god} 판단

2. 응답 형식:
   {{
     "personality": "성격 분석",
     "fortune_2024": "올해 운세",
     "advice": "구체적 조언"
   }}

생년월일시: {birth_info}
질문: {question}
"""
```

### **2. 로직 제어 한계**

---

Bedrock Agent의 커스텀 한계점을 상세히 비교 분석하는 스크립트를 생성합니다.

---


## 🎯 **핵심 한계점 요약**

### **1. 프롬프트 엔지니어링 한계** ❌
```python
# Bedrock Agent - 단순함
instruction = "You are a fortune teller"

# 현재 구현 - 정교함  
prompt = f"""
사주명리학 전문가로서 다음 규칙을 따라주세요:
1. 일간 {day_master}의 강약 판단
2. 월령 {season}에 따른 용신 선정
3. 대운 {current_luck}과의 상호작용 분석
4. 구체적 시기와 조언 제시

응답 형식: {json_schema}
"""
```

### **2. 멀티에이전트 구현 불가** ❌
- Agent는 단일 역할만 수행
- 현재 구현: 7개 전문 에이전트 협업

### **3. 실시간 데이터 연동 제한** ❌
- MCP 연동 복잡 (Action Group 필요)
- 현재 구현: 직접 subprocess 호출

### **4. 응답 형식 제어 어려움** ❌
```python
# Agent: 텍스트만
"올해 운세가 좋습니다..."

# 현재: 구조화된 JSON
{
  "agent_type": "saju",
  "saju_analysis": {...},
  "consultation": "...",
  "confidence": 0.85
}
```

## 🏆 **결론**

**Bedrock Agent는 일반적인 챗봇에는 좋지만, 사주 상담처럼 전문적이고 복잡한 도메인에는 커스텀 한계가 치명적입니다.**

현재 구현이 훨씬 우수한 이유:
- ✅ **완전한 제어권**
- ✅ **전문 도메인 최적화** 
- ✅ **멀티에이전트 아키텍처**
- ✅ **유연한 확장성**
- ✅ **정확한 비용 예측**