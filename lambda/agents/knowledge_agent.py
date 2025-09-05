from typing import Dict, Any

class KnowledgeAgent:
    def __init__(self):
        # 확장된 RAG 기반 명리학 지식베이스
        self.knowledge_base = {
            "elements_interaction": {
                # 상생 관계
                "wood_fire": "목생화 - 목이 화를 돕는 관계, 창의성과 열정이 조화",
                "fire_earth": "화생토 - 화가 토를 생성, 열정이 안정으로 전환",
                "earth_metal": "토생금 - 토가 금을 생성, 안정이 성과로 연결",
                "metal_water": "금생수 - 금이 수를 생성, 성과가 지혜로 승화",
                "water_wood": "수생목 - 수가 목을 생성, 지혜가 성장력으로 발전",
                # 상극 관계
                "wood_earth": "목극토 - 목이 토를 극하는 관계, 도전정신 필요",
                "fire_metal": "화극금 - 화가 금을 극하는 관계, 변화와 혁신",
                "earth_water": "토극수 - 토가 수를 극하는 관계, 실용성 중시",
                "metal_wood": "금극목 - 금이 목을 극하는 관계, 원칙과 규율",
                "water_fire": "수극화 - 수가 화를 극하는 관계, 냉정과 열정의 균형"
            },
            "bazi_combinations": {
                "갑자_을축": "해중금 조합 - 재물운 상승, 금융업 적성",
                "병인_정묘": "화목 조합 - 명예운 발달, 창작 분야 유리",
                "무진_기사": "토화 조합 - 안정적 발전, 부동산 관련",
                "경오_신미": "금토 조합 - 지도력 발휘, 경영 적성",
                "임신_계유": "수금 조합 - 지혜와 전략, IT 분야 유리"
            },
            "career_interpretations": {
                "관성강": "공직, 관리직, 법조계 적합 - 질서와 원칙을 중시",
                "식상강": "창작, 기술, 교육 분야 유리 - 아이디어와 표현력",
                "재성강": "사업, 금융, 영업 적합 - 수익 창출 능력",
                "인성강": "연구, 의료, 상담 분야 유리 - 학습과 도움",
                "비견강": "독립사업, 전문직 적합 - 자유로운 환경 선호"
            },
            "fortune_patterns": {
                "대운상승": "10년간 상승운 - 새로운 도전, 직업 변화 적기",
                "대운하강": "10년간 하강운 - 안정 추구, 기존 기반 강화",
                "세운길": "올해 길운 - 적극적 행동, 새로운 시작",
                "세운흉": "올해 흉운 - 신중한 판단, 안전 중시",
                "월운길": "이번 달 길운 - 단기 성과, 좋은 소식",
                "월운흉": "이번 달 흉운 - 주의 필요, 감정 조절"
            },
            "compatibility_patterns": {
                "상생궁합": "서로 도움이 되는 관계 - 장기적 안정",
                "상극궁합": "자극적이지만 성장하는 관계 - 도전과 발전",
                "비화궁합": "비슷한 성향으로 안정적 - 평화로운 관계",
                "충극궁합": "강한 대립과 갈등 - 신중한 접근 필요"
            }
        }
    
    def get_bazi_interpretation(self, bazi_data: Dict[str, Any], category: str) -> str:
        """고도화된 RAG 기반 사주 해석"""
        interpretations = []
        
        # 1. 기본 사주 분석
        year_pillar = bazi_data.get('year_pillar', '')
        if year_pillar:
            interpretations.append(f"년주 {year_pillar} 기본 성향 분석")
        
        # 2. 오행 상호작용 분석
        elements_analysis = self._analyze_elements_interaction(bazi_data)
        if elements_analysis:
            interpretations.append(elements_analysis)
        
        # 3. 카테고리별 전문 해석
        if category == "career":
            career_analysis = self._get_career_analysis(bazi_data)
            interpretations.append(career_analysis)
        elif category == "love" or category == "marriage":
            compatibility_analysis = self._get_compatibility_analysis(bazi_data)
            interpretations.append(compatibility_analysis)
        elif category in ["finance", "health", "general"]:
            fortune_analysis = self._get_fortune_analysis(bazi_data)
            interpretations.append(fortune_analysis)
        
        # 4. 사주 조합 특수 해석
        combination_analysis = self._analyze_special_combinations(bazi_data)
        if combination_analysis:
            interpretations.append(combination_analysis)
        
        return " | ".join(filter(None, interpretations))
    
    def _analyze_elements_interaction(self, bazi_data: Dict[str, Any]) -> str:
        """오행 상호작용 분석"""
        elements = bazi_data.get('elements', '')
        if not elements:
            return ""
        
        element_list = [e.strip() for e in elements.split(',')]
        interactions = []
        
        for i, elem1 in enumerate(element_list):
            for elem2 in element_list[i+1:]:
                interaction_key = f"{elem1}_{elem2}"
                reverse_key = f"{elem2}_{elem1}"
                
                interaction = (self.knowledge_base["elements_interaction"].get(interaction_key) or 
                             self.knowledge_base["elements_interaction"].get(reverse_key))
                if interaction:
                    interactions.append(interaction)
        
        return "; ".join(interactions[:2])  # 상위 2개만 표시
    
    def _get_career_analysis(self, bazi_data: Dict[str, Any]) -> str:
        """직업 전문 분석"""
        career_pattern = self._analyze_career_pattern(bazi_data)
        base_analysis = self.knowledge_base["career_interpretations"].get(
            career_pattern, "직업 적성 분석 필요"
        )
        
        # MCP 데이터 활용
        if bazi_data.get('mcp_used'):
            dayun = bazi_data.get('dayun', [])
            if dayun:
                base_analysis += f" | 현재 대운 기간: 직업 변화에 유리"
        
        return base_analysis
    
    def _get_compatibility_analysis(self, bazi_data: Dict[str, Any]) -> str:
        """궁합 전문 분석"""
        elements = bazi_data.get('elements', '')
        if '목' in elements and '화' in elements:
            return self.knowledge_base["compatibility_patterns"]["상생궁합"]
        elif '금' in elements and '목' in elements:
            return self.knowledge_base["compatibility_patterns"]["상극궁합"]
        else:
            return self.knowledge_base["compatibility_patterns"]["비화궁합"]
    
    def _get_fortune_analysis(self, bazi_data: Dict[str, Any]) -> str:
        """운세 전문 분석"""
        fortune_pattern = self._analyze_fortune_pattern(bazi_data)
        base_analysis = self.knowledge_base["fortune_patterns"].get(
            fortune_pattern, "운세 분석 필요"
        )
        
        # MCP 데이터의 대운/세운 정보 활용
        if bazi_data.get('mcp_used'):
            liunian = bazi_data.get('liunian', {})
            if liunian:
                base_analysis += f" | 올해 세운: 중요한 변화 예상"
        
        return base_analysis
    
    def _analyze_special_combinations(self, bazi_data: Dict[str, Any]) -> str:
        """특수 사주 조합 분석"""
        year_pillar = bazi_data.get('year_pillar', '')
        month_pillar = bazi_data.get('month_pillar', '')
        
        if year_pillar and month_pillar:
            combination_key = f"{year_pillar}_{month_pillar}"
            combination = self.knowledge_base["bazi_combinations"].get(combination_key)
            if combination:
                return f"특수 조합: {combination}"
        
        return ""
    
    def _analyze_career_pattern(self, bazi_data: Dict[str, Any]) -> str:
        """직업 패턴 분석"""
        # 간단한 패턴 분석 (실제로는 더 복잡)
        elements = bazi_data.get('elements', '목')
        
        if '금' in elements:
            return "관성강"
        elif '화' in elements:
            return "식상강"
        elif '토' in elements:
            return "재성강"
        elif '수' in elements:
            return "인성강"
        
        return "일반"
    
    def _analyze_fortune_pattern(self, bazi_data: Dict[str, Any]) -> str:
        """정교한 운세 패턴 분석"""
        # MCP 데이터 활용
        if bazi_data.get('mcp_used'):
            dayun = bazi_data.get('dayun', [])
            liunian = bazi_data.get('liunian', {})
            
            if dayun and len(dayun) > 0:
                current_dayun = dayun[0] if isinstance(dayun, list) else dayun
                # 대운 분석 로직
                if '길' in str(current_dayun):
                    return "대운상승"
                elif '흉' in str(current_dayun):
                    return "대운하강"
            
            if liunian:
                # 세운 분석 로직
                if '길' in str(liunian):
                    return "세운길"
                elif '흉' in str(liunian):
                    return "세운흉"
        
        # 기본 분석 (폴백)
        elements = bazi_data.get('elements', '')
        if '금' in elements or '수' in elements:
            return "세운길"
        elif '화' in elements or '토' in elements:
            return "대운상승"
        else:
            return "세운흉"