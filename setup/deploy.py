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

    # 출력에서 URL 추출
    api_url = None
    backend_url = None
    backend_ip = None
    
    for line in output.split('\n'):
        if "ApiGatewayUrl" in line and "=" in line:
            api_url = line.split("=")[1].strip()
        elif "BackendUrl" in line and "=" in line:
            backend_url = line.split("=")[1].strip()
        elif "BackendPublicIP" in line and "=" in line:
            backend_ip = line.split("=")[1].strip()
    
    print(f"\n✅ 배포 완료!")
    if api_url:
        print(f"📡 API Gateway: {api_url}")
        print(f"🔗 사주 상담 URL: {api_url}saju")
    
    if backend_url:
        print(f"🚀 Backend 서버: {backend_url}")
        print(f"🔍 Backend Health: {backend_url}/health")
    
    if backend_ip:
        print(f"\n💻 Backend 배포 대기 중... (IP: {backend_ip})")
        print("🕰️ EC2 인스턴스가 시작되고 Docker 컴포즈가 실행될 때까지 3-5분 소요")
        
        # Backend 서버 상태 확인
        import time
        import requests
        
        print("🔍 Backend 서버 상태 확인 중...")
        for i in range(30):  # 5분 대기
            try:
                response = requests.get(f"http://{backend_ip}:3001/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Backend 서버 준비 완료! ({i*10}초 소요)")
                    break
            except:
                pass
            print(f"⏳ Backend 서버 시작 대기 중... ({i*10}/300초)")
            time.sleep(10)
        else:
            print("⚠️ Backend 서버 상태 확인 시간 초과. 수동으로 확인해주세요.")

    # 테스트 예제 출력
    print("\n📋 테스트 예제:")
    if api_url:
        print(f"""
# API Gateway 테스트
curl -X POST {api_url}saju/basic \\
  -H "Content-Type: application/json" \\
  -d '{{
    "birth_info": {{
      "year": 1990,
      "month": 5,
      "day": 15,
      "hour": 14
    }},
    "name": "테스트사용자"
  }}'
        """)
    
    if backend_url:
        print(f"""
# Backend 직접 테스트
curl -X POST {backend_url}/api/saju \\
  -H "Content-Type: application/json" \\
  -d '{{
    "birthDate": "1990-05-15",
    "birthTime": "14:00",
    "gender": "male",
    "name": "테스트사용자"
  }}'
        """)


def destroy():
    """리소스 삭제 (순서대로)"""
    print("🗑️ 리소스 삭제 중...")
    cdk_dir = os.path.join(os.getcwd(), "cdk")
    
    # Backend 서버 중지 (선택사항)
    try:
        print("🚀 Backend 서버 중지 시도...")
        # EC2 인스턴스에서 Docker 컴포즈 중지
        # 이는 CDK destroy에서 처리되므로 선택사항
        pass
    except Exception as e:
        print(f"⚠️ Backend 서버 중지 실패: {e}")
    
    # CDK 스택 삭제
    print("📋 CDK 스택 삭제 중...")
    try:
        run_command("cdk destroy --force", cwd=cdk_dir)
        print("✅ CDK 스택 삭제 완료")
    except Exception as e:
        print(f"❌ CDK 스택 삭제 실패: {e}")
        
        # 수동 리소스 정리 시도
        print("🔧 수동 리소스 정리 시도...")
        try:
            cleanup_resources()
        except Exception as cleanup_error:
            print(f"❌ 수동 정리도 실패: {cleanup_error}")
            raise e
    
    print("✅ 리소스 삭제 완료")


def redeploy():
    """완전 재배포 (삭제 후 배포)"""
    print("🔄 완전 재배포 시작")
    
    # 기존 리소스 삭제
    try:
        destroy()
    except Exception as e:
        print(f"기존 리소스 삭제 실패: {e}")
        print("수동으로 리소스를 확인하고 삭제해주세요.")
        return
    
    print("\n⏳ 120초 대기 (리소스 완전 삭제 확인)...")
    import time
    time.sleep(120)
    
    # 새로 배포
    deploy()


def cleanup_resources():
    """수동 리소스 정리 (VPC 의존성 순서대로)"""
    import boto3
    import time
    
    print("🧹 수동 리소스 정리 시작 (순서: Lambda → EC2 → ElastiCache → 보안그룹 → VPC)")
    
    # 1단계: Lambda 함수 삭제
    try:
        lambda_client = boto3.client('lambda')
        functions = lambda_client.list_functions()
        for func in functions['Functions']:
            if 'yedamo' in func['FunctionName'].lower():
                print(f"Lambda 함수 삭제: {func['FunctionName']}")
                lambda_client.delete_function(FunctionName=func['FunctionName'])
        time.sleep(10)
    except Exception as e:
        print(f"Lambda 정리 실패: {e}")
    
    # 2단계: EC2 인스턴스 종료
    try:
        ec2 = boto3.client('ec2')
        instances = ec2.describe_instances(
            Filters=[{'Name': 'tag:Name', 'Values': ['*Yedamo*', '*yedamo*']}]
        )
        instance_ids = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] not in ['terminated', 'terminating']:
                    instance_ids.append(instance['InstanceId'])
        
        if instance_ids:
            print(f"EC2 인스턴스 종료: {instance_ids}")
            ec2.terminate_instances(InstanceIds=instance_ids)
            print("⏳ EC2 종료 대기 (60초)...")
            time.sleep(60)
    except Exception as e:
        print(f"EC2 정리 실패: {e}")
    
    # 3단계: ElastiCache 클러스터 삭제
    try:
        elasticache = boto3.client('elasticache')
        clusters = elasticache.describe_cache_clusters()
        for cluster in clusters['CacheClusters']:
            if 'yedamo' in cluster['CacheClusterId'].lower():
                print(f"ElastiCache 클러스터 삭제: {cluster['CacheClusterId']}")
                elasticache.delete_cache_cluster(
                    CacheClusterId=cluster['CacheClusterId']
                )
        
        # 서브넷 그룹 삭제
        subnet_groups = elasticache.describe_cache_subnet_groups()
        for sg in subnet_groups['CacheSubnetGroups']:
            if 'yedamo' in sg['CacheSubnetGroupName'].lower():
                print(f"ElastiCache 서브넷 그룹 삭제: {sg['CacheSubnetGroupName']}")
                elasticache.delete_cache_subnet_group(
                    CacheSubnetGroupName=sg['CacheSubnetGroupName']
                )
        
        print("⏳ ElastiCache 삭제 대기 (60초)...")
        time.sleep(60)
    except Exception as e:
        print(f"ElastiCache 정리 실패: {e}")
    
    # 4단계: 보안 그룹 삭제
    try:
        security_groups = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': ['*Yedamo*', '*yedamo*']}]
        )
        for sg in security_groups['SecurityGroups']:
            if sg['GroupName'] != 'default':
                print(f"보안 그룹 삭제: {sg['GroupId']} ({sg['GroupName']})")
                try:
                    ec2.delete_security_group(GroupId=sg['GroupId'])
                except Exception as sg_error:
                    print(f"보안 그룹 삭제 실패: {sg_error}")
        time.sleep(10)
    except Exception as e:
        print(f"보안 그룹 정리 실패: {e}")
    
    # 5단계: VPC 삭제
    try:
        vpcs = ec2.describe_vpcs(
            Filters=[{'Name': 'tag:Name', 'Values': ['*Yedamo*', '*yedamo*']}]
        )
        for vpc in vpcs['Vpcs']:
            vpc_id = vpc['VpcId']
            print(f"VPC 삭제: {vpc_id}")
            
            # 서브넷 삭제
            subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            for subnet in subnets['Subnets']:
                print(f"서브넷 삭제: {subnet['SubnetId']}")
                ec2.delete_subnet(SubnetId=subnet['SubnetId'])
            
            # 인터넷 게이트웨이 삭제
            igws = ec2.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
            )
            for igw in igws['InternetGateways']:
                print(f"인터넷 게이트웨이 디타치: {igw['InternetGatewayId']}")
                ec2.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=vpc_id)
                ec2.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])
            
            # VPC 삭제
            ec2.delete_vpc(VpcId=vpc_id)
            
    except Exception as e:
        print(f"VPC 정리 실패: {e}")
    
    # 6단계: CloudFormation 스택 삭제
    try:
        cf = boto3.client('cloudformation')
        stacks = cf.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'DELETE_FAILED'])
        for stack in stacks['StackSummaries']:
            if 'yedamo' in stack['StackName'].lower():
                print(f"CloudFormation 스택 삭제: {stack['StackName']}")
                cf.delete_stack(StackName=stack['StackName'])
                print("⏳ 스택 삭제 대기 (60초)...")
                time.sleep(60)
    except Exception as e:
        print(f"CloudFormation 스택 정리 실패: {e}")
    
    print("✅ 수동 리소스 정리 완료")


def deploy_backend_only():
    """백엔드만 재배포 (개발용)"""
    print("🚀 Backend 서버 재배포...")
    
    # CDK 출력에서 Backend IP 가져오기
    cdk_dir = os.path.join(os.getcwd(), "cdk")
    try:
        output = run_command("cdk deploy --require-approval never --outputs-file outputs.json", cwd=cdk_dir)
        
        # outputs.json에서 IP 추출
        import json
        with open(os.path.join(cdk_dir, "outputs.json"), 'r') as f:
            outputs = json.load(f)
        
        backend_ip = outputs.get('YedamoStack', {}).get('BackendPublicIP')
        if not backend_ip:
            print("❌ Backend IP를 찾을 수 없습니다.")
            return
        
        print(f"💻 Backend IP: {backend_ip}")
        print("🕰️ SSH로 연결하여 수동 재배포하세요:")
        print(f"ssh -i yedamo-key-pair.pem ec2-user@{backend_ip}")
        print("cd yedamo-aws-hackathon/backend && docker-compose down && docker-compose up -d --build")
        
    except Exception as e:
        print(f"❌ Backend 재배포 실패: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "destroy":
            destroy()
        elif sys.argv[1] == "redeploy":
            redeploy()
        elif sys.argv[1] == "cleanup":
            cleanup_resources()
        elif sys.argv[1] == "backend":
            deploy_backend_only()
        else:
            print("사용법: python deploy.py [destroy|redeploy|cleanup|backend]")
    else:
        deploy()
