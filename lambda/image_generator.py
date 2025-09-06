import json
import boto3
import base64
from typing import Dict, Any

# 12지신 동물 목록
ZODIAC_ANIMALS = [
    "쥐", "소", "호랑이", "토끼", "용", "뱀", 
    "말", "양", "원숭이", "닭", "개", "돼지"
]

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    try:
        # CORS 헤더
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        # OPTIONS 요청 처리
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        color = body.get('color', '').strip()
        animal = body.get('animal', '').strip()
        
        # 입력 검증
        if not color or not animal:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'color와 animal 파라미터가 필요합니다.',
                    'required_animals': ZODIAC_ANIMALS
                })
            }
        
        if animal not in ZODIAC_ANIMALS:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': f'유효하지 않은 동물입니다. 12지신 중 하나를 선택해주세요.',
                    'valid_animals': ZODIAC_ANIMALS
                })
            }
        
        # 프롬프트 생성
        prompt = f"A beautiful {color} colored {animal} in traditional Korean art style, elegant and mystical, high quality digital art"
        
        # Bedrock 클라이언트 생성
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Nova Canvas 모델 호출
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0,
                "seed": 42
            }
        }
        
        response = bedrock.invoke_model(
            modelId='amazon.nova-canvas-v1:0',
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        # 응답 처리
        response_body = json.loads(response['body'].read())
        
        if 'images' in response_body and len(response_body['images']) > 0:
            # Base64 인코딩된 이미지 데이터
            image_data = response_body['images'][0]
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'prompt': prompt,
                    'color': color,
                    'animal': animal,
                    'image': image_data,
                    'format': 'base64'
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': '이미지 생성에 실패했습니다.',
                    'details': response_body
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': f'서버 오류: {str(e)}'
            })
        }
