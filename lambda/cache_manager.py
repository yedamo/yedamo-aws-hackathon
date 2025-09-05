import json
import time
import redis
import os
from typing import Dict, Any, Optional, Tuple

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', '6379')),
            decode_responses=True
        )
        self.TTL = 30 * 60  # 30분
        self.REFRESH_THRESHOLD = 5 * 60  # 5분
    
    def generate_cache_key(self, name: str) -> str:
        """캐시 키 생성 (timestamp_name)"""
        timestamp = int(time.time())
        return f"{timestamp}_{name}"
    
    def set_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """캐시 저장"""
        cache_data = {
            'data': data,
            'timestamp': int(time.time())
        }
        self.redis_client.setex(
            cache_key,
            self.TTL,
            json.dumps(cache_data, ensure_ascii=False)
        )
    
    def get_cache(self, cache_key: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        """캐시 조회 (데이터, 갱신필요여부)"""
        cached_json = self.redis_client.get(cache_key)
        if not cached_json:
            return None, False
        
        cached_item = json.loads(cached_json)
        current_time = int(time.time())
        age = current_time - cached_item['timestamp']
        
        # 갱신 필요 확인 (만료 5분 미만)
        needs_refresh = age > (self.TTL - self.REFRESH_THRESHOLD)
        
        return cached_item['data'], needs_refresh
    
    def refresh_cache(self, cache_key: str) -> None:
        """캐시 타임스탬프 갱신"""
        cached_json = self.redis_client.get(cache_key)
        if cached_json:
            cached_item = json.loads(cached_json)
            cached_item['timestamp'] = int(time.time())
            self.redis_client.setex(
                cache_key,
                self.TTL,
                json.dumps(cached_item, ensure_ascii=False)
            )

# 전역 캐시 매니저
cache_manager = CacheManager()