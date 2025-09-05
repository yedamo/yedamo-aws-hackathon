import json
import boto3
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    
    @abstractmethod
    def get_system_prompt(self):
        """각 에이전트별 시스템 프롬프트"""
        pass
    
    def calculate_saju_basic(self, birth_info):
        """기본 사주 계산"""
        year = birth_info.get('year')
        month = birth_info.get('month')
        day = birth_info.get('day')
        hour = birth_info.get('hour', 12)
        
        heavenly_stems = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        earthly_branches = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
        
        year_stem = heavenly_stems[(year - 4) % 10]
        year_branch = earthly_branches[(year - 4) % 12]
        
        return {
            'year_pillar': f'{year_stem}{year_branch}',
            'birth_date': f'{year}년 {month}월 {day}일',
            'year': year, 'month': month, 'day': day, 'hour': hour
        }
    
    def invoke_bedrock(self, prompt):
        """Bedrock 호출"""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        except Exception as e:
            return f"AI 처리 중 오류: {str(e)}"
    
    @abstractmethod
    def process(self, birth_info, question):
        """각 에이전트별 처리 로직"""
        pass