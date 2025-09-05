#!/usr/bin/env python3
"""
예다모 사주 상담 서비스 배포 스크립트
"""
import subprocess
import sys
import os


def run_command(command, cwd=None):
    """명령어 실행"""
    print(f"실행 중: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"오류: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    return result.stdout


def deploy():
    """배포 실행"""
    print("🚀 예다모 사주 상담 서비스 배포 시작")

    # CDK 디렉토리로 이동
    cdk_dir = os.path.join(os.getcwd(), "cdk")

    # 의존성 설치
    print("\n📦 의존성 설치 중...")
    run_command("pip3 install -r requirements.txt", cwd=cdk_dir)

    # CDK 부트스트랩 (처음 한 번만 필요)
    print("\n🔧 CDK 부트스트랩...")
    try:
        run_command("cdk bootstrap", cwd=cdk_dir)
    except:
        print("부트스트랩 이미 완료됨")

    # CDK 배포
    print("\n🌟 스택 배포 중...")
    output = run_command("cdk deploy --require-approval never", cwd=cdk_dir)

    # API URL 추출
    if "YedamoStack.YedamoApiEndpoint" in output:
        api_url = output.split("YedamoStack.YedamoApiEndpoint")[
            1].split("=")[1].strip()
        print(f"\n✅ 배포 완료!")
        print(f"📡 API 엔드포인트: {api_url}")
        print(f"🔗 사주 상담 URL: {api_url}saju")

        # 테스트 예제 출력
        print("\n📋 테스트 예제:")
        print(f"""
curl -X POST {api_url}saju \\
  -H "Content-Type: application/json" \\
  -d '{{
    "birth_info": {{
      "year": 1990,
      "month": 5,
      "day": 15,
      "hour": 14
    }},
    "question": "올해 운세는 어떤가요?"
  }}'
        """)


def destroy():
    """리소스 삭제"""
    print("🗑️ 리소스 삭제 중...")
    cdk_dir = os.path.join(os.getcwd(), "cdk")
    run_command("cdk destroy --force", cwd=cdk_dir)
    print("✅ 리소스 삭제 완료")


def redeploy():
    """완전 재배포 (삭제 후 배포)"""
    print("🔄 완전 재배포 시작")
    
    # 기존 리소스 삭제
    try:
        destroy()
    except:
        print("기존 리소스 없음 또는 삭제 실패")
    
    print("\n⏳ 5초 대기...")
    import time
    time.sleep(5)
    
    # 새로 배포
    deploy()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "destroy":
            destroy()
        elif sys.argv[1] == "redeploy":
            redeploy()
        else:
            print("사용법: python deploy.py [destroy|redeploy]")
    else:
        deploy()
