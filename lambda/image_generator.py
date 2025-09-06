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
        gender = body.get('gender', 'neutral')
        dominant_element = body.get('dominant_element', '')
        
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
        
        # 동물 매핑 (한국어 -> 영어)
        animal_mapping = {
            '쥐': 'mouse', '소': 'ox', '호랑이': 'tiger', '토끼': 'rabbit',
            '용': 'dragon', '뱀': 'snake', '말': 'horse', '양': 'sheep',
            '원숭이': 'monkey', '닭': 'rooster', '개': 'dog', '돼지': 'pig'
        }
        
        # 오행별 배경 컨셉 매핑
        element_backgrounds = {
            'wood': 'lush green forest background with ancient trees and glowing leaves',
            'fire': 'volcanic landscape with glowing lava and flame effects in background',
            'earth': 'mountain cave with crystal formations and earthy stone textures',
            'metal': 'shimmering metallic temple with golden reflections and sharp geometric patterns',
            'water': 'serene lake with waterfalls and misty clouds in mystical blue atmosphere',
            'balanced': 'harmonious mystical landscape with elements of all five elements'
        }
        
        # 오행별 동물 스타일 매핑
        element_styles = {
            'wood': 'nature-infused, with leaf patterns on fur/scales',
            'fire': 'flame-like markings, glowing ember effects',
            'earth': 'rocky texture, crystal embedded',
            'metal': 'metallic sheen, armor-like scales',
            'water': 'flowing, translucent, bubble effects',
            'balanced': 'harmonious blend of all elemental features'
        }
        
        # 성별 스타일 매핑
        gender_styles = {
            'male': 'strong, powerful',
            'female': 'elegant, graceful',
            'neutral': 'balanced'
        }
        
        # 프롬프트 생성
        english_animal = animal_mapping.get(animal, animal)
        
        # 포켓몬 스타일 기본 프롬프트
        base_prompt = f"Cute chibi-style {english_animal} pokemon-like creature with {color} coloring"
        
        # 배경 설정
        background = element_backgrounds.get(dominant_element, 'mystical fantasy background')
        
        # 동물 스타일 요소들
        style_elements = []
        
        if dominant_element and dominant_element in element_styles:
            style_elements.append(element_styles[dominant_element])
            
        if gender in gender_styles:
            style_elements.append(gender_styles[gender])
        
        # 최종 프롬프트 조합
        style_part = ', '.join(style_elements) if style_elements else 'adorable'
        prompt = f"{base_prompt}, {style_part}, {background}, kawaii anime art style, highly detailed, soft lighting, no humans"
        
        # Bedrock 클라이언트 생성
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Nova Canvas 모델 호출
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": "human, person, people, man, woman, face, hands, realistic, dark, scary, ugly"
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0
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
                    'gender': gender,
                    'dominant_element': dominant_element,
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
