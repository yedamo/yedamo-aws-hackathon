#!/usr/bin/env python3
"""
Independent Saju Image Generation API Test Script
"""

import requests
import json
import base64
import sys
from datetime import datetime

def test_image_generation(api_url, test_data):
    """Test image generation API"""
    print(f"🧪 Testing API: {api_url}")
    print(f"📝 Test data: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=180
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Image generation successful!")
                print(f"🎨 Prompt: {data.get('prompt', 'N/A')}")
                print(f"🐾 Animal: {data.get('animal', 'N/A')}")
                print(f"🎨 Color: {data.get('color', 'N/A')}")
                
                # Save image if needed
                if '--save' in sys.argv and data.get('image'):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_image_{timestamp}.png"
                    
                    with open(filename, 'wb') as f:
                        f.write(base64.b64decode(data['image']))
                    print(f"💾 Image saved as: {filename}")
                
                return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (>180s)")
        return False
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        return False

def main():
    # Default API URL (update after deployment)
    api_url = "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/generate"
    
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    # Test data
    test_cases = [
        {
            "name": "Golden Dragon (Male, Metal dominant)",
            "data": {
                "animal": "용",
                "color": "금색",
                "gender": "male",
                "elements": {
                    "wood": 1,
                    "fire": 2,
                    "earth": 1,
                    "metal": 3,
                    "water": 1
                },
                "dominant_element": "metal",
                "yin_yang_balance": "yang_dominant"
            }
        },
        {
            "name": "Pink Rabbit (Female, Wood dominant)",
            "data": {
                "animal": "토끼",
                "color": "분홍색",
                "gender": "female",
                "elements": {
                    "wood": 3,
                    "fire": 1,
                    "earth": 1,
                    "metal": 1,
                    "water": 2
                },
                "dominant_element": "wood",
                "yin_yang_balance": "yin_dominant"
            }
        }
    ]
    
    print("🚀 Starting Independent Saju Image API Tests")
    print("=" * 50)
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        if test_image_generation(api_url, test_case['data']):
            success_count += 1
        
        if i < len(test_cases):
            print("\n⏳ Waiting 5 seconds before next test...")
            import time
            time.sleep(5)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{len(test_cases)} passed")
    
    if success_count == len(test_cases):
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
