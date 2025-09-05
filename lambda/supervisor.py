import json
import boto3
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from agents.saju_agent import SajuAgent
from agents.fortune_agent import FortuneAgent
from agents.compatibility_agent import CompatibilityAgent
from agents.question_analyzer import QuestionAnalyzer
from agents.response_generator import ResponseGenerator
from agents.knowledge_agent import KnowledgeAgent

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

class AgentType(Enum):
    SAJU_AGENT = "saju"
    FORTUNE_AGENT = "fortune"
    COMPATIBILITY_AGENT = "compatibility"
    QUESTION_ANALYZER = "question_analyzer"
    RESPONSE_GENERATOR = "response_generator"
    KNOWLEDGE_AGENT = "knowledge_agent"

@dataclass
class UserContext:
    birth_info: Optional[Dict[str, Any]] = None
    question: Optional[str] = None
    bazi_data: Optional[Dict[str, Any]] = None
    analysis_result: Optional[Dict[str, Any]] = None
    language: str = "ko"

class SupervisorAgent:
    def __init__(self):
        self.agents = {
            AgentType.SAJU_AGENT: SajuAgent(),
            AgentType.FORTUNE_AGENT: FortuneAgent(),
            AgentType.COMPATIBILITY_AGENT: CompatibilityAgent(),
            AgentType.QUESTION_ANALYZER: QuestionAnalyzer(),
            AgentType.RESPONSE_GENERATOR: ResponseGenerator(),
            AgentType.KNOWLEDGE_AGENT: KnowledgeAgent()
        }
        self.context = UserContext()
    
    def route_request(self, birth_info, question):
        """통합 멀티에이전트 처리 - 모든 개선사항 적용"""
        try:
            # 컨텍스트 설정
            self.context.birth_info = birth_info
            self.context.question = question
            
            # 1. 지능형 질문 분석
            analysis_result = self.agents[AgentType.QUESTION_ANALYZER].analyze(question)
            self.context.analysis_result = analysis_result
            
            # 2. MCP 지원 사주 데이터 생성 (폴백 메커니즘 포함)
            try:
                bazi_data = self.agents[AgentType.SAJU_AGENT].get_bazi_info(birth_info)
                self.context.bazi_data = bazi_data
            except Exception as e:
                # 폴백: 기본 사주 계산
                bazi_data = self.agents[AgentType.SAJU_AGENT].calculate_saju_basic(birth_info)
                self.context.bazi_data = bazi_data
            
            # 3. RAG 지식베이스 활용 해석
            knowledge_interpretation = self.agents[AgentType.KNOWLEDGE_AGENT].get_bazi_interpretation(
                self.context.bazi_data, 
                analysis_result.get('category', 'general')
            )
            
            # 4. 에이전트 라우팅 및 처리
            agent_type = self._classify_request(question, analysis_result)
            
            # 5. 전문 에이전트 처리
            if agent_type == AgentType.SAJU_AGENT:
                specialist_result = self.agents[AgentType.SAJU_AGENT].process(birth_info, question)
            elif agent_type == AgentType.FORTUNE_AGENT:
                specialist_result = self.agents[AgentType.FORTUNE_AGENT].process(birth_info, question)
            elif agent_type == AgentType.COMPATIBILITY_AGENT:
                specialist_result = self.agents[AgentType.COMPATIBILITY_AGENT].process(birth_info, question)
            else:
                specialist_result = None
            
            # 6. 통합 응답 생성 (전문 에이전트 + RAG + 분석 결과 종합)
            if specialist_result and 'error' not in specialist_result:
                # 전문 에이전트 결과에 RAG 지식 추가
                enhanced_result = self._enhance_with_knowledge(specialist_result, knowledge_interpretation)
                return enhanced_result
            else:
                # 통합 응답 생성기 사용
                return self.agents[AgentType.RESPONSE_GENERATOR].generate_response(self.context)
                
        except Exception as e:
            return {
                "error": f"Supervisor 처리 오류: {str(e)}",
                "agent_type": "supervisor",
                "consultation": "상담 중 오류가 발생했습니다. 다시 시도해주세요."
            }
    
    def _enhance_with_knowledge(self, specialist_result, knowledge_interpretation):
        """전문 에이전트 결과에 RAG 지식 추가"""
        if isinstance(specialist_result, dict) and 'consultation' in specialist_result:
            enhanced_consultation = f"{specialist_result['consultation']}\n\n[명리학 전문 지식]\n{knowledge_interpretation}"
            specialist_result['consultation'] = enhanced_consultation
            specialist_result['enhanced_with_rag'] = True
        
        return specialist_result
    
    def _classify_request(self, question, analysis_result=None):
        """지능형 질문 분류 - QuestionAnalyzer 결과 우선 활용"""
        # 1단계: QuestionAnalyzer 결과 활용 (지능형 라우팅)
        if analysis_result:
            category = analysis_result.get('category', 'general')
            urgency = analysis_result.get('urgency', 'short_term')
            
            # 카테고리와 긴급도에 따른 에이전트 선택
            if category in ['love', 'marriage'] or '연애' in question or '결혼' in question:
                return AgentType.COMPATIBILITY_AGENT
            elif category in ['career', 'finance', 'health'] or urgency == 'immediate':
                return AgentType.FORTUNE_AGENT
            elif category == 'general' or '사주' in question or '성격' in question:
                return AgentType.SAJU_AGENT
        
        # 2단계: Bedrock 기반 분류 (폴백)
        try:
            prompt = f"""
다음 질문을 분석하여 적절한 에이전트를 선택해주세요:

질문: {question}

에이전트 종류:
- saju: 기본 사주팔자 분석, 성격, 타고난 운명
- fortune: 운세 예측, 대운, 세운, 월운 관련
- compatibility: 궁합, 인간관계, 연애, 결혼 관련

응답은 반드시 다음 중 하나만: saju, fortune, compatibility
"""
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            agent_type = result['content'][0]['text'].strip().lower()
            
            if agent_type == 'saju':
                return AgentType.SAJU_AGENT
            elif agent_type == 'fortune':
                return AgentType.FORTUNE_AGENT
            elif agent_type == 'compatibility':
                return AgentType.COMPATIBILITY_AGENT
                
        except Exception as e:
            print(f"Bedrock 분류 오류: {e}")
        
        # 3단계: 기본 폴백
        return AgentType.SAJU_AGENT