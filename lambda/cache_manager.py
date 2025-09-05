import json
import time
from typing import Dict, Any, Optional, Tuple

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.TTL = 30 * 60  # 30분
        self.REFRESH_THRESHOLD = 5 * 60  # 5분
    
    def generate_cache_key(self, name: str) -> str:
        """캐시 키 생성 (timestamp_name)"""
        timestamp = int(time.time())
        return f"{timestamp}_{name}"
    
    def set_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """캐시 저장"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': int(time.time())
        }
    
    def get_cache(self, cache_key: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        """캐시 조회 (데이터, 갱신필요여부)"""
        if cache_key not in self.cache:
            return None, False
        
        cached_item = self.cache[cache_key]
        current_time = int(time.time())
        age = current_time - cached_item['timestamp']
        
        # TTL 만료 확인
        if age > self.TTL:
            del self.cache[cache_key]
            return None, False
        
        # 갱신 필요 확인 (만료 5분 미만)
        needs_refresh = age > (self.TTL - self.REFRESH_THRESHOLD)
        
        return cached_item['data'], needs_refresh
    
    def refresh_cache(self, cache_key: str) -> None:
        """캐시 타임스탬프 갱신"""
        if cache_key in self.cache:
            self.cache[cache_key]['timestamp'] = int(time.time())

# 전역 캐시 매니저
cache_manager = CacheManager()