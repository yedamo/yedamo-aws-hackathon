import json
import os
import requests

# Backend API URL
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:3001')


def handler(event, context):
    try:
        path = event.get('path', '')
        body = json.loads(event['body'])

        if path == '/saju/basic':
            return handle_basic_saju(body)
        elif path == '/saju/consultation':
            return handle_consultation_proxy(body)
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
    """기본 사주 정보 반환 API - Backend 서버 호출"""
    birth_info = validate_birth_info(body)
    name = body.get('name', '')

    if not name:
        raise ValueError('name이 필요합니다')

    # Backend API 호출
    try:
        # birth_info를 backend 형식으로 변환
        backend_payload = {
            'birthDate': f"{birth_info['year']}-{birth_info['month']:02d}-{birth_info['day']:02d}",
            'birthTime': f"{birth_info['hour']:02d}:00",
            'isLunar': birth_info.get('isLunar', False),
            'gender': birth_info.get('gender', 'male'),
            'name': name
        }

        response = requests.post(
            f"{BACKEND_URL}/saju/basic",
            json=backend_payload,
            timeout=30
        )

        if response.status_code == 200:
            backend_data = response.json()

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'cache_key': backend_data.get('cache_key'),
                    'birth_info': birth_info,
                    'saju_analysis': backend_data.get('data', {}),
                    'backend_response': backend_data
                }, ensure_ascii=False)
            }
        else:
            raise Exception(
                f"Backend API 오류: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Backend 서버 연결 실패: {str(e)}")
    except Exception as e:
        raise Exception(f"사주 데이터 처리 실패: {str(e)}")


def handle_consultation_proxy(body):
    """상담 API - EC2 Backend로 프록시"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/saju/consultation",
            json=body,
            timeout=30
        )

        return {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response.json(), ensure_ascii=False)
        }

    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Backend 연결 실패: {str(e)}'}, ensure_ascii=False)
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
        raise ValueError('연도는 1900-2100 사이여야 합니다')
    if not (1 <= month <= 12):
        raise ValueError('월은 1-12 사이여야 합니다')
    if not (1 <= day <= 31):
        raise ValueError('일은 1-31 사이여야 합니다')
    if not (0 <= hour <= 23):
        raise ValueError('시간은 0-23 사이여야 합니다')

    return birth_info
