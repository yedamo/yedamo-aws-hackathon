#!/usr/bin/env python3
"""
새로운 API 형식 테스트 클라이언트
"""
import requests
import json

def test_basic_saju(api_url):
    """기본 사주 정보 API 테스트"""
    print("🔮 기본 사주 정보 조회 테스트")
    
    test_data = {
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "gender": "male",
            "timezone": "Asia/Shanghai"
        }
    }
    
    print(f"📅 생년월일: {test_data['birth_info']['year']}년 {test_data['birth_info']['month']}월 {test_data['birth_info']['day']}일 {test_data['birth_info']['hour']}시")
    print("⏳ 사주 계산 중...")
    
    try:
        response = requests.post(
            f"{api_url}/saju/basic",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 사주 계산 완료!")
            print(f"📊 사주 분석: {json.dumps(result['saju_analysis'], ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 연결 오류: {str(e)}")

def test_consultation(api_url):
    """질의응답 API 테스트"""
    print("\n💬 질의응답 테스트")
    
    test_data = {
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "gender": "male"
        },
        "question": "올해 운세와 직장운이 어떤가요?"
    }
    
    print(f"❓ 질문: {test_data['question']}")
    print("⏳ 멀티에이전트 상담 중...")
    
    try:
        response = requests.post(
            f"{api_url}/saju/consultation",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 상담 완료!")
            print(f"🤖 에이전트: {result.get('agent_type', 'unknown')}")
            print(f"🎯 상담 결과: {result.get('consultation', 'N/A')}")
        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 연결 오류: {str(e)}")

if __name__ == "__main__":
    print("🔮 예다모 AI 사주 상담사 - 새로운 API 테스트")
    api_url = input("API URL을 입력하세요: ").strip()
    if not api_url:
        print("API URL이 필요합니다.")
        exit(1)
    
    test_basic_saju(api_url)
    test_consultation(api_url)