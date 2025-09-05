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
        """MCP 데이터를 표준 형식으로 변환"""
        # 원본 데이터에서 사주팔자 정보 추출
        bazi = mcp_data.get('四柱', {})
        wuxing = mcp_data.get('五行', {})
        
        # 오행 분석 생성
        total_elements = sum(wuxing.values()) if wuxing else 8
        wuxing_analysis = []
        element_names = {'木': '목', '火': '화', '土': '토', '金': '금', '水': '수'}
        
        for element, count in wuxing.items():
            korean_name = element_names.get(element, element)
            percentage = (count / total_elements * 100) if total_elements > 0 else 0
            strength = "강함" if count >= 3 else "보통" if count == 2 else "약함"
            wuxing_analysis.append(f"{korean_name}: {count}개 ({percentage:.1f}%) - {strength}")
        
        return {
            "success": True,
            "data": {
                "name": "사용자",
                "translatedData": {
                    "사주팔자": {
                        "년주": bazi.get('年柱', '미상'),
                        "월주": bazi.get('月柱', '미상'),
                        "일주": bazi.get('日柱', '미상'),
                        "시주": bazi.get('时柱', '미상')
                    },
                    "오행": {element_names.get(k, k): v for k, v in wuxing.items()},
                    "띠": mcp_data.get('生肖', '미상'),
                    "별자리": mcp_data.get('星座', '미상'),
                    "일주천간": mcp_data.get('日主', '미상'),
                    "원본데이터": mcp_data
                },
                "wuxingAnalysis": wuxing_analysis,
                "rawData": {
                    "content": [{"type": "text", "text": json.dumps(mcp_data, ensure_ascii=False)}],
                    "isError": False
                }
            }
        }

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
        basic_data = {
            "四柱": {
                "年柱": f"{birth_info['year']}년주",
                "月柱": f"{birth_info['month']}월주", 
                "日柱": f"{birth_info['day']}일주",
                "时柱": f"{birth_info['hour']}시주"
            },
            "五行": {"木": 1, "火": 2, "土": 2, "金": 1, "水": 2},
            "生肖": "미상",
            "星座": "미상",
            "日主": "미상"
        }
        
        return {
            "success": True,
            "data": {
                "name": "사용자",
                "translatedData": {
                    "사주팔자": {
                        "년주": basic_data["四柱"]["年柱"],
                        "월주": basic_data["四柱"]["月柱"],
                        "일주": basic_data["四柱"]["日柱"],
                        "시주": basic_data["四柱"]["时柱"]
                    },
                    "오행": {"목": 1, "화": 2, "토": 2, "금": 1, "수": 2},
                    "띠": "미상",
                    "별자리": "미상",
                    "일주천간": "미상",
                    "원본데이터": basic_data
                },
                "wuxingAnalysis": [
                    "목: 1개 (12.5%) - 약함",
                    "화: 2개 (25.0%) - 보통", 
                    "토: 2개 (25.0%) - 보통",
                    "금: 1개 (12.5%) - 약함",
                    "수: 2개 (25.0%) - 보통"
                ],
                "rawData": {
                    "content": [{"type": "text", "text": json.dumps(basic_data, ensure_ascii=False)}],
                    "isError": False
                }
            }
        }

    def process(self, birth_info, question):
        # 통합 사주 데이터 생성
        saju_data = self.get_bazi_info(birth_info)
        
        # 사주 데이터에서 상담 내용 생성
        translated_data = saju_data.get("data", {}).get("translatedData", {})
        saju_info = translated_data.get("사주팔자", {})
        wuxing_analysis = saju_data.get("data", {}).get("wuxingAnalysis", [])
        
        prompt = f"""
{self.get_system_prompt()}

생년월일시: {birth_info}
사주팔자: {saju_info}
오행분석: {wuxing_analysis}
질문: {question}

사주팔자를 바탕으로 성격, 재능, 기본 운명을 분석해주세요.
"""

        consultation = self.invoke_bedrock(prompt)
        
        # 기존 사주 데이터에 상담 내용 추가
        result = saju_data.copy()
        result["data"]["consultation"] = consultation
        result["agent_type"] = "saju"
        
        return result
