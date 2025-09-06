#!/usr/bin/env python3
import requests
import json
import base64
import sys
from datetime import datetime

def test_image_generation(api_url, color, animal):
    """이미지 생성 API 테스트"""
    
    endpoint = f"{api_url}/image"
    
    payload = {
        "color": color,
        "animal": animal
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🎨 {color} {animal} 이미지 생성 요청...")
    print(f"📡 API 엔드포인트: {endpoint}")
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=180)
        
        print(f"📊 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ 이미지 생성 성공!")
                print(f"🎯 프롬프트: {result.get('prompt')}")
                print(f"🎨 색상: {result.get('color')}")
                print(f"🐉 동물: {result.get('animal')}")
                
                # Base64 이미지 데이터 저장
                if result.get('image'):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_{color}_{animal}_{timestamp}.png"
                    
                    # Base64 디코딩 후 파일 저장
                    image_data = base64.b64decode(result['image'])
                    with open(filename, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"💾 이미지 저장: {filename}")
                    return True
            else:
                print(f"❌ 이미지 생성 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ API 호출 실패: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ 요청 시간 초과 (3분)")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

def main():
    # API URL (배포 후 실제 URL로 변경 필요)
    api_url = input("API Gateway URL을 입력하세요 (예: https://abc123.execute-api.us-east-1.amazonaws.com/prod): ").strip()
    
    if not api_url:
        print("❌ API URL이 필요합니다.")
        sys.exit(1)
    
    # 12지신 동물 목록
    animals = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
    
    print("🐉 지원되는 12지신 동물:")
    for i, animal in enumerate(animals, 1):
        print(f"{i:2d}. {animal}")
    
    print("\n🎨 테스트 예시:")
    
    # 테스트 케이스들
    test_cases = [
        ("빨간", "용"),
        ("파란", "호랑이"),
        ("금색", "닭")
    ]
    
    for color, animal in test_cases:
        print(f"\n{'='*50}")
        success = test_image_generation(api_url, color, animal)
        if not success:
            print(f"⚠️  {color} {animal} 테스트 실패")
        print("⏳ 3초 대기...")
        import time
        time.sleep(3)
    
    print(f"\n{'='*50}")
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    main()
