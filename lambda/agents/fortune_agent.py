import json
from .base_agent import BaseAgent

class FortuneAgent(BaseAgent):
    def get_system_prompt(self):
        return """당신은 운세 예측 전문가입니다.
사주팔자를 바탕으로 대운, 세운, 월운을 분석하여
구체적인 시기별 운세를 예측해주세요."""
    
    def process(self, birth_info, question):
        saju_basic = self.calculate_saju_basic(birth_info)
        current_year = 2024
        age = current_year - saju_basic['year'] + 1
        
        prompt = f"""
{self.get_system_prompt()}

생년월일시: {saju_basic['year']}년 {saju_basic['month']}월 {saju_basic['day']}일 {saju_basic['hour']}시
현재 나이: {age}세
질문: {question}

다음 형식으로 JSON 응답해주세요:
{{
  "agent_type": "fortune",
  "saju_analysis": {{
    "year_pillar": "년주",
    "current_age": {age},
    "daeun_period": "현재 대운",
    "birth_date": "{saju_basic['birth_date']}"
  }},
  "consultation": "올해 운세, 내년 전망, 월별 운세 등 시기별 상세 분석"
}}
"""
        
        response = self.invoke_bedrock(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "agent_type": "fortune",
                "saju_analysis": {**saju_basic, "current_age": age},
                "consultation": response
            }