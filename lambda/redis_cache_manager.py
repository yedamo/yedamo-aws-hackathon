import json
import time
import os
from typing import Dict, Any, Optional, Tuple

class RedisCacheManager:
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = int(os.environ.get('REDIS_PORT', '6379'))
        self.TTL = int(os.environ.get('CACHE_TTL', '1800'))  # 30분
        self.REFRESH_THRESHOLD = int(os.environ.get('CACHE_REFRESH_THRESHOLD', '300'))  # 5분
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Redis 연결 (redis 모듈 없이 간단 구현)"""
        try:
            # Redis 모듈이 없으면 메모리 캐시로 폴백
            import redis
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            print(f"Redis 연결 성공: {self.redis_host}:{self.redis_port}")
        except ImportError:
            print("Redis 모듈 없음, 메모리 캐시 사용")
            self.redis_client = None
            self.memory_cache = {}
        except Exception as e:
            print(f"Redis 연결 실패, 메모리 캐시 사용: {e}")
            self.redis_client = None
            self.memory_cache = {}
    
    def generate_cache_key(self, name: str) -> str:
        """캐시 키 생성 (timestamp_name)"""
        timestamp = int(time.time())
        return f"{timestamp}_{name}"
    
    def set_cache(self, cache_key: str, data: Dict[str, Any]) -> bool:
        """캐시 저장"""
        cache_data = {
            'data': data,
            'timestamp': int(time.time())
        }
        
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key,
                    self.TTL,
                    json.dumps(cache_data, ensure_ascii=False)
                )
                return True
            except Exception as e:
                print(f"Redis 캐시 저장 실패: {e}")
        
        # 메모리 캐시 폴백
        self.memory_cache[cache_key] = cache_data
        return True
    
    def get_cache(self, cache_key: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        """캐시 조회 (데이터, 갱신필요여부)"""
        cached_item = None
        
        if self.redis_client:
            try:
                cached_json = self.redis_client.get(cache_key)
                if cached_json:
                    cached_item = json.loads(cached_json)
            except Exception as e:
                print(f"Redis 캐시 조회 실패: {e}")
        
        # 메모리 캐시 폴백
        if not cached_item and hasattr(self, 'memory_cache'):
            cached_item = self.memory_cache.get(cache_key)
        
        if not cached_item:
            return None, False
        
        current_time = int(time.time())
        age = current_time - cached_item['timestamp']
        
        # TTL 만료 확인
        if age > self.TTL:
            if self.redis_client:
                try:
                    self.redis_client.delete(cache_key)
                except:
                    pass
            elif hasattr(self, 'memory_cache'):
                self.memory_cache.pop(cache_key, None)
            return None, False
        
        # 갱신 필요 확인
        needs_refresh = age > (self.TTL - self.REFRESH_THRESHOLD)
        return cached_item['data'], needs_refresh
    
    def refresh_cache(self, cache_key: str) -> bool:
        """캐시 타임스탬프 갱신"""
        if self.redis_client:
            try:
                cached_json = self.redis_client.get(cache_key)
                if cached_json:
                    cached_item = json.loads(cached_json)
                    cached_item['timestamp'] = int(time.time())
                    self.redis_client.setex(
                        cache_key,
                        self.TTL,
                        json.dumps(cached_item, ensure_ascii=False)
                    )
                    return True
            except Exception as e:
                print(f"Redis 캐시 갱신 실패: {e}")
        
        # 메모리 캐시 폴백
        if hasattr(self, 'memory_cache') and cache_key in self.memory_cache:
            self.memory_cache[cache_key]['timestamp'] = int(time.time())
            return True
        
        return False

# 전역 캐시 매니저
redis_cache_manager = RedisCacheManager()