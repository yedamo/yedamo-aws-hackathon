import json
import os
from supervisor import SupervisorAgent
from agents.saju_agent import SajuAgent

# 환경에 따른 캐시 매니저 선택
if os.environ.get('REDIS_HOST'):
    from redis_cache_manager import redis_cache_manager as cache_manager
else:
    from cache_manager import cache_manager


def handler(event, context):
    try:
        path = event.get('path', '')
        body = json.loads(event['body'])

        if path == '/saju/basic':
            return handle_basic_saju(body)
        elif path == '/saju/consultation':
            return handle_consultation(body)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Path not found'}, ensure_ascii=False)
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)}, ensure_ascii=False)
        }


def handle_basic_saju(body):
    """기본 사주 정보 반환 API"""
    birth_info = validate_birth_info(body)
    name = body.get('name', '')

    if not name:
        raise ValueError('name이 필요합니다')

    # 캐시 키 생성
    cache_key = cache_manager.generate_cache_key(name)

    # 사주 데이터 계산
    saju_agent = SajuAgent()
    saju_data = saju_agent.get_bazi_info(birth_info)

    # 캐시 저장
    cache_manager.set_cache(cache_key, {
        'birth_info': birth_info,
        'saju_analysis': saju_data
    })

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'cache_key': cache_key,
            'birth_info': birth_info,
            'saju_analysis': saju_data
        }, ensure_ascii=False)
    }


def handle_consultation(body):
    """질의응답 API"""
    cache_key = body.get('cache_key', '')
    question = body.get('question', '')

    if not cache_key:
        raise ValueError('cache_key가 필요합니다')
    if not question:
        raise ValueError('질문이 필요합니다')

    # 캐시에서 사주 데이터 조회
    cached_data, needs_refresh = cache_manager.get_cache(cache_key)

    if not cached_data:
        raise ValueError('캐시된 사주 데이터가 없습니다. 기본 사주 API를 먼저 호출하세요.')

    # 갱신 필요 시 캐시 갱신
    if needs_refresh:
        cache_manager.refresh_cache(cache_key)

    # 멀티에이전트 상담
    supervisor = SupervisorAgent()
    result = supervisor.route_request(cached_data['birth_info'], question)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result, ensure_ascii=False)
    }


def validate_birth_info(body):
    """사용자 정보 검증 (기본 사주 API용)"""
    birth_info = body.get('birth_info', {})

    # 필수 필드 검증
    required_fields = ['year', 'month', 'day', 'hour']
    for field in required_fields:
        if field not in birth_info:
            raise ValueError(f'{field}가 필요합니다')

    # 범위 검증
    year = birth_info['year']
    month = birth_info['month']
    day = birth_info['day']
    hour = birth_info['hour']

    if not (1900 <= year <= 2100):
        raise ValueError('년도는 1900-2100 범위여야 합니다')
    if not (1 <= month <= 12):
        raise ValueError('월은 1-12 범위여야 합니다')
    if not (1 <= day <= 31):
        raise ValueError('일은 1-31 범위여야 합니다')
    if not (0 <= hour <= 23):
        raise ValueError('시간은 0-23 범위여야 합니다')

    # 선택 필드 기본값 설정
    birth_info.setdefault('gender', 'male')
    birth_info.setdefault('timezone', 'Asia/Shanghai')

    return birth_info

# Supervisor와 멀티에이전트가 모든 로직을 처리
