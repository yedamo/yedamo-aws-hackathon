from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_elasticache as elasticache,
    aws_ec2 as ec2,
    Duration,
)
from constructs import Construct

class YedamoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC 생성 (ElastiCache용)
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

        # ElastiCache 서브넷 그룹 (의존성 명시)
        cache_subnet_group = elasticache.CfnSubnetGroup(
            self, "YedamoCacheSubnetGroup",
            description="Subnet group for Yedamo cache",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )
        
        # VPC 서브넷에 대한 의존성 명시적 설정
        for subnet in vpc.private_subnets:
            cache_subnet_group.node.add_dependency(subnet)

        # ElastiCache 보안 그룹
        cache_security_group = ec2.SecurityGroup(
            self, "YedamoCacheSecurityGroup",
            vpc=vpc,
            description="Security group for ElastiCache",
            allow_all_outbound=False
        )

        # Lambda 보안 그룹
        lambda_security_group = ec2.SecurityGroup(
            self, "YedamoLambdaSecurityGroup",
            vpc=vpc,
            description="Security group for Lambda"
        )

        # Lambda에서 ElastiCache로의 접근 허용
        cache_security_group.add_ingress_rule(
            peer=lambda_security_group,
            connection=ec2.Port.tcp(6379),
            description="Allow Lambda to access Redis"
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
        
        # 의존성 명시적 설정
        redis_cluster.add_dependency(cache_subnet_group)

        # Lambda 실행 역할
        lambda_role = iam.Role(
            self, "YedamoLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
            ],
            inline_policies={
                "BedrockAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["bedrock:InvokeModel"],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

        # Lambda 함수 (멀티에이전트 + 캐시 지원)
        saju_lambda = _lambda.Function(
            self, "SajuLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.seconds(60),
            memory_size=512,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[lambda_security_group],
            environment={
                "MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
                "SUPERVISOR_ENABLED": "true",
                "REDIS_HOST": redis_cluster.attr_redis_endpoint_address,
                "REDIS_PORT": "6379",
                "CACHE_TTL": "1800",  # 30분
                "CACHE_REFRESH_THRESHOLD": "300"  # 5분
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

        # API 리소스 및 메서드
        saju_resource = api.root.add_resource("saju")
        saju_integration = apigw.LambdaIntegration(saju_lambda)
        
        # 기본 사주 API
        basic_resource = saju_resource.add_resource("basic")
        basic_resource.add_method("POST", saju_integration)
        
        # 질의응답 API
        consultation_resource = saju_resource.add_resource("consultation")
        consultation_resource.add_method("POST", saju_integration)

        # ElastiCache CLI용 베스천 호스트
        bastion_security_group = ec2.SecurityGroup(
            self, "YedamoBastionSecurityGroup",
            vpc=vpc,
            description="Security group for bastion host"
        )
        
        # SSH 접근 허용
        bastion_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="SSH access"
        )
        
        # 베스천에서 ElastiCache 접근 허용
        cache_security_group.add_ingress_rule(
            peer=bastion_security_group,
            connection=ec2.Port.tcp(6379),
            description="Allow bastion to access Redis"
        )
        
        # 베스천 호스트 인스턴스
        bastion_host = ec2.Instance(
            self, "YedamoBastionHost",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=bastion_security_group,
            key_name="yedamo-key-pair",
            user_data=ec2.UserData.custom(
                "#!/bin/bash\n"
                "yum update -y\n"
                "yum install -y redis\n"
                "echo 'Redis CLI 설치 완료' > /home/ec2-user/redis-ready.txt"
            )
        )
        
        # 출력
        self.api_url = api.url
        self.redis_endpoint = redis_cluster.attr_redis_endpoint_address
        self.bastion_public_ip = bastion_host.instance_public_ip