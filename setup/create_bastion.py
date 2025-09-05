#!/usr/bin/env python3
import boto3


def create_bastion_host():
    ec2 = boto3.client('ec2')

    # VPC와 퍼블릭 서브넷 찾기
    vpc_id = 'vpc-065afde29f6c4edb3'  # YedamoStack VPC

    # 퍼블릭 서브넷 찾기
    subnets = ec2.describe_subnets(
        Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'tag:aws-cdk:subnet-type', 'Values': ['Public']}
        ]
    )

    if not subnets['Subnets']:
        print("퍼블릭 서브넷을 찾을 수 없습니다.")
        return

    public_subnet_id = subnets['Subnets'][0]['SubnetId']

    # 보안 그룹 생성
    sg_response = ec2.create_security_group(
        GroupName='elasticache-bastion-sg',
        Description='Bastion host for ElastiCache access',
        VpcId=vpc_id
    )

    security_group_id = sg_response['GroupId']

    # SSH 접근 허용
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )

    # EC2 인스턴스 생성
    response = ec2.run_instances(
        ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='yedamo-key-pair',
        SecurityGroupIds=[security_group_id],
        SubnetId=public_subnet_id,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'elasticache-bastion'}]
            }
        ],
        UserData='''#!/bin/bash
yum update -y
yum install -y redis
'''
    )

    instance_id = response['Instances'][0]['InstanceId']

    print(f"베스천 호스트 생성됨: {instance_id}")
    print(f"보안 그룹: {security_group_id}")
    print("인스턴스가 실행되면 SSH로 접속 후 redis-cli 사용 가능")


def remove_bastion_host():
    ec2 = boto3.client('ec2')

    # 베스천 호스트 찾기
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['elasticache-bastion']},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
        ]
    )

    # 보안 그룹 찾기
    security_groups = ec2.describe_security_groups(
        Filters=[
            {'Name': 'group-name', 'Values': ['elasticache-bastion-sg']}
        ]
    )

    # 인스턴스 종료
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(f"인스턴스 종료 중: {instance_id}")
            ec2.terminate_instances(InstanceIds=[instance_id])

    # 보안 그룹 삭제 (인스턴스 종료 후 잠시 대기 필요)
    for sg in security_groups['SecurityGroups']:
        sg_id = sg['GroupId']
        print(f"보안 그룹 삭제 예정: {sg_id} (인스턴스 종료 완료 후 수동 삭제 필요)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'remove':
        remove_bastion_host()
    else:
        create_bastion_host()
