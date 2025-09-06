from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_elasticache as elasticache,
    aws_ec2 as ec2,
    Duration,
    CfnOutput,
)
from constructs import Construct


class YedamoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC 생성
        vpc = ec2.Vpc(
            self, "YedamoVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # ElastiCache 서브넷 그룹
        cache_subnet_group = elasticache.CfnSubnetGroup(
            self, "YedamoCacheSubnetGroup",
            description="Subnet group for Yedamo cache",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )

        # ElastiCache 보안 그룹
        cache_security_group = ec2.SecurityGroup(
            self, "YedamoCacheSecurityGroup",
            vpc=vpc,
            description="Security group for ElastiCache",
            allow_all_outbound=False
        )

        # ElastiCache Redis 클러스터
        redis_cluster = elasticache.CfnCacheCluster(
            self, "YedamoRedisCluster",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=cache_subnet_group.ref,
            vpc_security_group_ids=[cache_security_group.security_group_id]
        )

        # Backend EC2 보안 그룹
        backend_security_group = ec2.SecurityGroup(
            self, "YedamoBackendSecurityGroup",
            vpc=vpc,
            description="Security group for Backend EC2"
        )

        # HTTP 및 SSH 접근 허용
        backend_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(3001),
            description="HTTP access to backend"
        )
        backend_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="SSH access"
        )

        # Backend에서 Redis 접근 허용
        cache_security_group.add_ingress_rule(
            peer=backend_security_group,
            connection=ec2.Port.tcp(6379),
            description="Allow backend to access Redis"
        )

        # Backend EC2 인스턴스 (Node.js + Bedrock)
        backend_instance = ec2.Instance(
            self, "YedamoBackendInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=backend_security_group,
            key_name="yedamo-key-pair",
            user_data=ec2.UserData.custom(
                "#!/bin/bash\n"
                "yum update -y\n"
                "yum install -y git aws-cli\n"
                
                # Node.js 18 설치
                "curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -\n"
                "yum install -y nodejs\n"
                "npm install -g pm2\n"
                
                # 환경변수 설정
                f"echo 'export REDIS_HOST={redis_cluster.attr_redis_endpoint_address}' >> /home/ec2-user/.bashrc\n"
                "echo 'export REDIS_PORT=6379' >> /home/ec2-user/.bashrc\n"
                "echo 'export AWS_REGION=us-east-1' >> /home/ec2-user/.bashrc\n"
                "echo 'export PORT=3001' >> /home/ec2-user/.bashrc\n"
                
                # 백엔드 시작 스크립트 생성
                "cat > /home/ec2-user/start-backend.sh << 'EOF'\n"
                "#!/bin/bash\n"
                "cd /home/ec2-user/yedamo-aws-hackathon/backend\n"
                f"export REDIS_HOST={redis_cluster.attr_redis_endpoint_address}\n"
                "export REDIS_PORT=6379\n"
                "export AWS_REGION=us-east-1\n"
                "export PORT=3001\n"
                "npm install\n"
                "pm2 start server.js --name yedamo-backend\n"
                "pm2 save\n"
                "pm2 startup\n"
                "EOF\n"
                "chmod +x /home/ec2-user/start-backend.sh\n"
                "chown ec2-user:ec2-user /home/ec2-user/start-backend.sh\n"
                
                "echo 'Backend setup completed. Run start-backend.sh after git clone.' > /home/ec2-user/backend-ready.txt\n"
            )
        )

        # Lambda 역할 (프록시용)
        lambda_role = iam.Role(
            self, "YedamoLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Lambda 함수 (프록시만)
        saju_lambda = _lambda.Function(
            self, "SajuLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "BACKEND_URL": f"http://{backend_instance.instance_public_ip}:3001"
            }
        )

        # API Gateway
        api = apigw.RestApi(
            self, "YedamoApi",
            rest_api_name="Yedamo Saju Service",
            description="AI 사주 상담 서비스",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )

        # API 리소스
        saju_resource = api.root.add_resource("saju")
        lambda_integration = apigw.LambdaIntegration(saju_lambda)
        
        # 모든 요청을 Lambda로 (Lambda가 EC2로 프록시)
        basic_resource = saju_resource.add_resource("basic")
        basic_resource.add_method("POST", lambda_integration)
        
        consultation_resource = saju_resource.add_resource("consultation")
        consultation_resource.add_method("POST", lambda_integration)

        # 출력
        CfnOutput(self, "ApiGatewayUrl", value=api.url)
        CfnOutput(self, "RedisHost", value=redis_cluster.attr_redis_endpoint_address)
        CfnOutput(self, "BackendUrl", value=f"http://{backend_instance.instance_public_ip}:3001")
        CfnOutput(self, "BackendPublicIP", value=backend_instance.instance_public_ip)
