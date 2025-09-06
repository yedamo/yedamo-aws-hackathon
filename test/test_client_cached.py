#!/usr/bin/env python3
"""
캐시 기반 API 테스트 클라이언트
"""
import requests
import json
import time


def test_cached_flow(api_url):
    """캐시 기반 플로우 테스트"""
    print("🔮 캐시 기반 사주 상담 테스트")

    # 1단계: 기본 사주 정보 조회 (캐시 생성)
    print("\n📊 1단계: 기본 사주 정보 조회")
    basic_data = {
        "name": "김다롬",
        "birth_info": {
            "year": 1997,
            "month": 5,
            "day": 19,
            "hour": 12,
            "gender": "female",
            "region": "korea"
        }
    }

    print(f"👤 이름: {basic_data['name']}")
    print(f"📅 생년월일: {basic_data['birth_info']['year']}년 {basic_data['birth_info']['month']}월 {basic_data['birth_info']['day']}일 {basic_data['birth_info']['hour']}시")

    try:
        response = requests.post(
            f"{api_url}/saju/basic",
            headers={"Content-Type": "application/json"},
            json=basic_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            cache_key = result['cache_key']
            print(f"✅ 사주 계산 완료! 캐시 키: {cache_key}")
            print(
                f"📊 사주 분석: {json.dumps(result, ensure_ascii=False, indent=2)}")

            # 2단계: 질의응답 (캐시 사용)
            test_consultation_with_cache(api_url, cache_key)

        else:
            print(f"❌ 오류: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ 연결 오류: {str(e)}")


def test_consultation_with_cache(api_url, cache_key):
    """캐시를 사용한 질의응답 테스트"""
    print(f"\n💬 2단계: 질의응답 (캐시 키: {cache_key})")

    questions = [
        "올해 운세는 어떤가요?",
        "직장운과 재물운이 궁금합니다.",
        "연애운은 어떤가요?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n❓ 질문 {i}: {question}")

        consultation_data = {
            "cache_key": cache_key,
            "question": question
        }

        try:
            response = requests.post(
                f"{api_url}/saju/consultation",
                headers={"Content-Type": "application/json"},
                json=consultation_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 상담 완료!")
                print(f"🤖 에이전트: {result.get('agent_type', 'unknown')}")
                print(f"🎯 상담 결과: {result.get('consultation', 'N/A')}")
            else:
                print(f"❌ 오류: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ 연결 오류: {str(e)}")

        # 질문 간 간격
        if i < len(questions):
            time.sleep(1)


def test_cache_expiry(api_url):
    """캐시 만료 테스트 (데모용)"""
    print("\n⏰ 캐시 만료 테스트")
    print("실제 환경에서는 30분 후 만료되지만, 테스트를 위해 짧은 시간으로 시뮬레이션")

    # 잘못된 캐시 키로 테스트
    invalid_cache_key = "1234567890_테스트"
    consultation_data = {
        "cache_key": invalid_cache_key,
        "question": "테스트 질문"
    }

    try:
        response = requests.post(
            f"{api_url}/saju/consultation",
            headers={"Content-Type": "application/json"},
            json=consultation_data,
            timeout=30
        )

        if response.status_code == 500:
            print("✅ 예상대로 캐시 만료 오류 발생")
            print(f"📝 응답: {response.text}")
        else:
            print(f"⚠️ 예상과 다른 응답: {response.status_code}")

    except Exception as e:
        print(f"❌ 연결 오류: {str(e)}")


if __name__ == "__main__":
    print("🔮 예다모 AI 사주 상담사 - 캐시 기반 API 테스트")
    print("✨ 캐시 TTL: 30분 | 갱신 임계값: 5분")

    api_url = input("API URL을 입력하세요: ").strip()
    if not api_url:
        print("API URL이 필요합니다.")
        exit(1)

    # test_cached_flow(api_url)
    # test_cache_expiry(api_url)
    cache_key = "1757137772_김다롬"
    test_consultation_with_cache(api_url, cache_key)
