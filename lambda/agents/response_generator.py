import json
import boto3
from typing import Dict, Any

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

class ResponseGenerator:
    def __init__(self):
        self.templates = {
            "career": {
                "ko": "직업운 분석: {bazi_analysis}\n향후 {time_scope}년간 {prediction}",
                "en": "Career Analysis: {bazi_analysis}\nNext {time_scope} years: {prediction}"
            },
            "love": {
                "ko": "애정운 분석: {bazi_analysis}\n{time_scope}년간 연애운: {prediction}",
                "en": "Love Analysis: {bazi_analysis}\n{time_scope} years romance: {prediction}"
            }
        }
    
    def generate_response(self, context) -> Dict[str, Any]:
        """멀티에이전트 결과를 종합한 통합 응답 생성"""
        if not all([context.bazi_data, context.analysis_result]):
            return {"error": "사주 정보와 질문 분석이 필요합니다."}
        
        # 여러 에이전트 결과를 종합한 통합 응답 생성
        prompt = f"""
당신은 전문 사주명리학자입니다. 다음 정보를 종합하여 전문적이고 상세한 상담을 제공해주세요.

[기본 정보]
생년월일: {context.birth_info}
질문: {context.question}

[지능형 질문 분석 결과]
카테고리: {context.analysis_result.get('category', 'general')}
시간 범위: {context.analysis_result.get('time_scope', 1)}년
긴급도: {context.analysis_result.get('urgency', 'short_term')}
키워드: {context.analysis_result.get('keywords', [])}

[MCP 기반 사주 데이터]
{context.bazi_data}

[상담 요구사항]
1. 사주팔자 기본 분석
2. 질문 카테고리에 맞는 전문 상담
3. 시간 범위에 맞는 운세 예측
4. 실용적인 조언 및 권고사항

다음 형식으로 JSON 응답해주세요:
{{
  "agent_type": "integrated_multi_agent",
  "saju_analysis": {{
    "birth_date": "생년월일",
    "category": "{context.analysis_result.get('category', 'general')}",
    "time_scope": {context.analysis_result.get('time_scope', 1)},
    "urgency": "{context.analysis_result.get('urgency', 'short_term')}",
    "mcp_enhanced": true,
    "analysis_keywords": {context.analysis_result.get('keywords', [])}
  }},
  "consultation": "지능형 분석 + MCP 사주 + RAG 지식을 종합한 전문 상담 내용"
}}
"""
        
        try:
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,  # 통합 응답을 위해 더 많은 토큰
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            response_text = result['content'][0]['text']
            
            try:
                parsed_result = json.loads(response_text)
                # 통합 응답 메타데이터 추가
                parsed_result['multi_agent_enhanced'] = True
                parsed_result['processing_pipeline'] = [
                    'QuestionAnalyzer',
                    'SajuAgent_MCP',
                    'KnowledgeAgent_RAG',
                    'ResponseGenerator'
                ]
                return parsed_result
            except:
                return {
                    "agent_type": "integrated_multi_agent",
                    "saju_analysis": {
                        "birth_date": str(context.birth_info),
                        "category": context.analysis_result.get('category', 'general'),
                        "mcp_enhanced": True
                    },
                    "consultation": response_text,
                    "multi_agent_enhanced": True
                }
                
        except Exception as e:
            return {
                "error": f"통합 응답 생성 오류: {str(e)}",
                "agent_type": "integrated_multi_agent",
                "consultation": "멀티에이전트 상담 중 오류가 발생했습니다. 다시 시도해주세요.",
                "fallback_used": True
            }