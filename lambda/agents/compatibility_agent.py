import json
from .base_agent import BaseAgent

class CompatibilityAgent(BaseAgent):
    def get_system_prompt(self):
        return """당신은 궁합 분석 전문가입니다.
사주팔자를 바탕으로 인간관계, 연애, 결혼, 사업 파트너십 등의 
궁합을 분석해주세요."""
    
    def process(self, birth_info, question):
        saju_basic = self.calculate_saju_basic(birth_info)
        
        prompt = f"""
{self.get_system_prompt()}

생년월일시: {saju_basic['year']}년 {saju_basic['month']}월 {saju_basic['day']}일 {saju_basic['hour']}시
질문: {question}

다음 형식으로 JSON 응답해주세요:
{{
  "agent_type": "compatibility",
  "saju_analysis": {{
    "year_pillar": "년주",
    "personality_type": "성격 유형",
    "relationship_style": "인간관계 스타일",
    "birth_date": "{saju_basic['birth_date']}"
  }},
  "consultation": "궁합 분석, 연애운, 결혼 적기, 좋은 상대 유형 등 관계 중심 분석"
}}
"""
        
        response = self.invoke_bedrock(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "agent_type": "compatibility",
                "saju_analysis": saju_basic,
                "consultation": response
            }