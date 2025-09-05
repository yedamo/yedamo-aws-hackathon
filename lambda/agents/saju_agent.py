import json
import subprocess
from typing import Dict, Any
from .base_agent import BaseAgent


class SajuAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.mcp_command = ["npx", "-y", "@mymcp-fun/bazi"]

    def get_system_prompt(self):
        return """당신은 사주팔자 전문 분석가입니다. 
생년월일시를 바탕으로 사주팔자를 정확히 계산하고, 
타고난 성격, 재능, 기본 운명을 분석해주세요."""

    def get_bazi_info(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """사주팔자, 대운, 세운 정보 조회 - MCP 우선, 폴백 메커니즘 지원"""
        try:
            print("MCP @mymcp-fun/bazi 호출 시도...")
            mcp_result = self._get_mcp_bazi_info(birth_info)
            mcp_result['mcp_used'] = True
            mcp_result['data_source'] = 'mcp_bazi_package'
            return mcp_result
        except Exception as e:
            print(f"MCP 호출 실패: {e}, 폴백 메커니즘 사용")
            basic_result = self.calculate_saju_basic(birth_info)
            basic_result['mcp_used'] = False
            basic_result['fallback_used'] = True
            basic_result['data_source'] = 'basic_calculation'
            return basic_result

    def _get_mcp_bazi_info(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """정밀한 MCP @mymcp-fun/bazi 패키지 호출"""
        # 기본 형식을 MCP 형식으로 변환
        birth_date = f"{birth_info['year']}-{birth_info['month']:02d}-{birth_info['day']:02d}"
        birth_time = f"{birth_info['hour']:02d}"

        # 지역별 timezone 매핑
        timezone_map = {
            "korea": "Asia/Seoul",
            "usa_east": "America/New_York", 
            "usa_west": "America/Los_Angeles",
            "china": "Asia/Shanghai",
            "japan": "Asia/Tokyo"
        }
        
        timezone = birth_info.get("timezone") or timezone_map.get(birth_info.get("region"), "Asia/Seoul")

        # MCP 명령어 구성
        cmd = self.mcp_command + [
            "--birth-date", birth_date,
            "--birth-time", birth_time,
            "--calendar", "solar",
            "--gender", birth_info.get("gender", "male"),
            "--timezone", timezone
        ]

        print(f"MCP 명령어: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=None,
            env=None
        )

        if result.returncode == 0:
            mcp_data = json.loads(result.stdout)
            if self._validate_mcp_data(mcp_data):
                return self._enhance_mcp_data(mcp_data)
            else:
                raise Exception("MCP 데이터 검증 실패")
        else:
            raise Exception(f"MCP 실행 오류: {result.stderr}")

    def _validate_mcp_data(self, data: Dict[str, Any]) -> bool:
        """MCP 데이터 검증"""
        required_fields = ['bazi', 'dayun', 'liunian']
        return all(field in data for field in required_fields)

    def _enhance_mcp_data(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 데이터 보강 및 표준화"""
        enhanced = {
            'year_pillar': mcp_data.get('bazi', {}).get('year', '미상'),
            'month_pillar': mcp_data.get('bazi', {}).get('month', '미상'),
            'day_pillar': mcp_data.get('bazi', {}).get('day', '미상'),
            'hour_pillar': mcp_data.get('bazi', {}).get('hour', '미상'),
            'elements': self._extract_elements(mcp_data.get('bazi', {})),
            'dayun': mcp_data.get('dayun', []),
            'liunian': mcp_data.get('liunian', {}),
            'raw_mcp_data': mcp_data
        }
        return enhanced

    def _extract_elements(self, bazi_data: Dict[str, Any]) -> str:
        """바지 데이터에서 오행 추출"""
        elements = []
        for pillar in ['year', 'month', 'day', 'hour']:
            pillar_data = bazi_data.get(pillar, '')
            if pillar_data and len(pillar_data) >= 2:
                stem = pillar_data[0]
                elements.append(self._stem_to_element(stem))

        return ', '.join(set(elements)) if elements else '미상'

    def _stem_to_element(self, stem: str) -> str:
        """천간을 오행으로 변환"""
        mapping = {
            '갑': '목', '을': '목',
            '병': '화', '정': '화',
            '무': '토', '기': '토',
            '경': '금', '신': '금',
            '임': '수', '계': '수'
        }
        return mapping.get(stem, '미상')

    def calculate_saju_basic(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """기본 사주 계산 (폴백)"""
        return {
            'year_pillar': f"{birth_info['year']}년주",
            'month_pillar': f"{birth_info['month']}월주",
            'day_pillar': f"{birth_info['day']}일주",
            'hour_pillar': f"{birth_info['hour']}시주",
            'elements': '기본 오행 분석',
            'birth_date': f"{birth_info['year']}-{birth_info['month']:02d}-{birth_info['day']:02d}"
        }

    def process(self, birth_info, question):
        # 통합 사주 데이터 생성
        saju_data = self.get_bazi_info(birth_info)

        prompt = f"""
{self.get_system_prompt()}

생년월일시: {birth_info}
사주 데이터: {saju_data}
질문: {question}

다음 형식으로 JSON 응답해주세요:
{{
  "agent_type": "saju",
  "saju_analysis": {{
    "year_pillar": "년주",
    "month_pillar": "월주",
    "day_pillar": "일주", 
    "hour_pillar": "시주",
    "elements": "오행분석",
    "birth_date": "생년월일"
  }},
  "consultation": "사주팔자 기반 성격과 타고난 운명 분석"
}}
"""

        response = self.invoke_bedrock(prompt)

        try:
            return json.loads(response)
        except:
            return {
                "agent_type": "saju",
                "saju_analysis": saju_data,
                "consultation": response
            }
