import re
from typing import Dict, Any

class QuestionAnalyzer:
    def __init__(self):
        self.patterns = {
            "career": ["이직", "퇴사", "직장", "취업", "승진", "사업"],
            "love": ["연애", "결혼", "이별", "만남", "배우자"],
            "health": ["건강", "병", "수술", "치료"],
            "finance": ["돈", "투자", "재산", "사업", "수입"]
        }
        
        self.urgency_patterns = {
            "immediate": ["당장", "지금", "오늘", "내일", "이번주"],
            "short_term": ["올해", "이번년", "몇개월", "반년"],
            "long_term": ["내년", "몇년", "장기적"]
        }
    
    def analyze(self, question: str) -> Dict[str, Any]:
        """사용자 질문을 분석하여 카테고리와 시간 범위 결정"""
        category = self._categorize_question(question)
        time_scope = self._determine_time_scope(question, category)
        urgency = self._assess_urgency(question)
        keywords = self._extract_keywords(question)
        
        return {
            "category": category,
            "time_scope": time_scope,
            "urgency": urgency,
            "keywords": keywords,
            "original_question": question
        }
    
    def _categorize_question(self, question: str) -> str:
        for category, keywords in self.patterns.items():
            if any(keyword in question for keyword in keywords):
                return category
        return "general"
    
    def _determine_time_scope(self, question: str, category: str) -> int:
        """질문 내용과 카테고리에 따라 분석할 년수 결정"""
        if category == "career":
            if any(word in question for word in ["이직", "퇴사"]):
                return 3  # 이직/퇴사는 3년
        elif category == "love":
            return 2  # 연애는 2년
        elif category == "finance":
            return 5  # 재정은 5년
        
        return 1  # 기본 1년
    
    def _assess_urgency(self, question: str) -> str:
        for urgency, patterns in self.urgency_patterns.items():
            if any(pattern in question for pattern in patterns):
                return urgency
        return "short_term"
    
    def _extract_keywords(self, question: str) -> list:
        # 간단한 키워드 추출
        words = re.findall(r'\b\w+\b', question)
        return [word for word in words if len(word) > 1]