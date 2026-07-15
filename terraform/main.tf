# Artispreneur — AWS Terraform
# Full stack: RDS PostgreSQL + Cognito + S3 + Lambda + API Gateway + CloudFront + ElastiCache + Bedrock

terraform {
  required_version = ">= 1.7"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
  backend "s3" {
    bucket  = "artispreneur-terraform-state"
    key     = "dev/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" { region = var.aws_region }

# === NETWORK ===
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "artispreneur-vpc" }
}
resource "aws_subnet" "a" {
  vpc_id = aws_vpc.main.id; cidr_block = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true
}
resource "aws_subnet" "b" {
  vpc_id = aws_vpc.main.id; cidr_block = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"
  map_public_ip_on_launch = true
}
resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id }
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route { cidr_block = "0.0.0.0/0"; gateway_id = aws_internet_gateway.main.id }
}
resource "aws_route_table_association" "a" { subnet_id = aws_subnet.a.id; route_table_id = aws_route_table.public.id }
resource "aws_route_table_association" "b" { subnet_id = aws_subnet.b.id; route_table_id = aws_route_table.public.id }

# === S3 ===
resource "aws_s3_bucket" "static" { bucket = "artispreneur-static-${var.environment}" }
resource "aws_s3_bucket_website_configuration" "static" {
  bucket = aws_s3_bucket.static.id
  index_document { suffix = "index.html" }
  error_document { key = "index.html" }
}
resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id
  block_public_acls = false; block_public_policy = false
  ignore_public_acls = false; restrict_public_buckets = false
}
resource "aws_s3_bucket_policy" "static" {
  bucket = aws_s3_bucket.static.id
  policy = jsonencode({Version="2012-10-17",Statement:[{Effect="Allow",Principal="*",Action="s3:GetObject",Resource="${aws_s3_bucket.static.arn}/*"}]})
}
resource "aws_s3_bucket" "outputs" { bucket = "artispreneur-outputs-${var.environment}" }
resource "aws_s3_bucket_lifecycle_configuration" "outputs" {
  bucket = aws_s3_bucket.outputs.id
  rule { id="archive"; status="Enabled"
    transition { days=90; storage_class="STANDARD_IA" }
    transition { days=365; storage_class="GLACIER" }
  }
}

# === RDS PostgreSQL ===
resource "aws_db_subnet_group" "main" { name="artispreneur-db"; subnet_ids=[aws_subnet.a.id,aws_subnet.b.id] }
resource "aws_security_group" "rds" {
  name="artispreneur-rds"; vpc_id=aws_vpc.main.id
  ingress { from_port=5432; to_port=5432; protocol="tcp"; cidr_blocks=["10.0.0.0/16"] }
}
resource "aws_db_instance" "main" {
  identifier="artispreneur-db"; engine="postgres"; engine_version="16.3"
  instance_class=var.db_instance_class; allocated_storage=20; max_allocated_storage=100
  storage_encrypted=true; db_name=var.db_name; username=var.db_username
  password=random_password.db.result; db_subnet_group_name=aws_db_subnet_group.main.name
  vpc_security_group_ids=[aws_security_group.rds.id]; publicly_accessible=true
  skip_final_snapshot=var.environment=="dev"
}
resource "random_password" "db" { length=32; special=false }

# === Cognito ===
resource "aws_cognito_user_pool" "main" {
  name="artispreneur-users"; auto_verified_attributes=["email"]
  username_attributes=["email"]
  password_policy { minimum_length=8; require_lowercase=true }
  account_recovery_setting { recovery_mechanism { name="verified_email"; priority=1 } }
}
resource "aws_cognito_user_pool_client" "main" {
  name="artispreneur-client"; user_pool_id=aws_cognito_user_pool.main.id
  generate_secret=false
  explicit_auth_flows=["ALLOW_USER_PASSWORD_AUTH","ALLOW_REFRESH_TOKEN_AUTH"]
}
resource "aws_cognito_user_pool_domain" "main" { domain="artispreneur-${var.environment}"; user_pool_id=aws_cognito_user_pool.main.id }

# === Lambda ===
resource "aws_iam_role" "lambda" {
  name="artispreneur-lambda"
  assume_role_policy=jsonencode({Version="2012-10-17",Statement:[{Effect="Allow",Principal:{Service="lambda.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy_attachment" "lambda_basic" { role=aws_iam_role.lambda.name; policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" }
resource "aws_iam_role_policy" "lambda" {
  name="artispreneur-lambda-policy"; role=aws_iam_role.lambda.id
  policy=jsonencode({Version="2012-10-17",Statement:[{Effect:"Allow",Action:["rds-data:*","s3:*","bedrock:InvokeModel","bedrock:InvokeModelWithResponseStream","cognito-idp:*","secretsmanager:GetSecretValue"],Resource:"*"}]})
}
data "archive_file" "lambda" { type="zip"; source_dir="${path.module}/../backend"; output_path="${path.module}/lambda.zip" }
resource "aws_lambda_function" "api" {
  filename=data.archive_file.lambda.output_path; function_name="artispreneur-api"
  role=aws_iam_role.lambda.arn; handler="main.handler"; runtime="python3.12"
  timeout=30; memory_size=256; source_code_hash=data.archive_file.lambda.output_base64sha256
  environment { variables={
    DB_HOST=aws_db_instance.main.address; DB_NAME=var.db_name; DB_USER=var.db_username
    DB_PASSWORD=random_password.db.result; S3_OUTPUTS=aws_s3_bucket.outputs.id
    COGNITO_POOL=aws_cognito_user_pool.main.id; COGNITO_CLIENT=aws_cognito_user_pool_client.main.id
    BEDROCK_MODEL="deepseek.deepseek-v3"; ENVIRONMENT=var.environment
  }}
}

# === API Gateway ===
resource "aws_apigatewayv2_api" "main" { name="artispreneur-api"; protocol_type="HTTP" }
resource "aws_apigatewayv2_stage" "main" { api_id=aws_apigatewayv2_api.main.id; name="$default"; auto_deploy=true }
resource "aws_apigatewayv2_integration" "lambda" { api_id=aws_apigatewayv2_api.main.id; integration_type="AWS_PROXY"; integration_uri=aws_lambda_function.api.invoke_arn }
resource "aws_apigatewayv2_route" "proxy" { api_id=aws_apigatewayv2_api.main.id; route_key="ANY /{proxy+}"; target="integrations/${aws_apigatewayv2_integration.lambda.id}" }
resource "aws_lambda_permission" "api" { statement_id="AllowAPI"; action="lambda:InvokeFunction"; function_name=aws_lambda_function.api.function_name; principal="apigateway.amazonaws.com"; source_arn="${aws_apigatewayv2_api.main.execution_arn}/*/*" }

# === CloudFront ===
resource "aws_cloudfront_distribution" "main" {
  origin { domain_name=aws_s3_bucket.static.bucket_regional_domain_name; origin_id="S3" }
  origin { domain_name=replace(aws_apigatewayv2_api.main.api_endpoint,"/^https?://([^/]*).*/","$1"); origin_id="API"
    custom_origin_config { http_port=80; https_port=443; origin_protocol_policy="https-only"; origin_ssl_protocols=["TLSv1.2"] } }
  enabled=true; default_root_object="index.html"; price_class="PriceClass_100"
  default_cache_behavior { target_origin_id="S3"; viewer_protocol_policy="redirect-to-https"
    allowed_methods=["GET","HEAD"]; cached_methods=["GET","HEAD"]
    forwarded_values { query_string=false; cookies { forward="none" } }; min_ttl=0; default_ttl=3600; max_ttl=86400 }
  ordered_cache_behavior { path_pattern="/api/*"; target_origin_id="API"; viewer_protocol_policy="redirect-to-https"
    allowed_methods=["DELETE","GET","HEAD","OPTIONS","PATCH","POST","PUT"]; cached_methods=["GET","HEAD"]
    forwarded_values { query_string=true; headers=["Authorization","Content-Type"]; cookies { forward="all" } }; min_ttl=0; default_ttl=0; max_ttl=0 }
  restrictions { geo_restriction { restriction_type="none" } }
  viewer_certificate { cloudfront_default_certificate=true }
}

# === ElastiCache ===
resource "aws_security_group" "redis" { name="artispreneur-redis"; vpc_id=aws_vpc.main.id
  ingress { from_port=6379; to_port=6379; protocol="tcp"; cidr_blocks=["10.0.0.0/16"] } }
resource "aws_elasticache_cluster" "main" { cluster_id="artispreneur-cache"; engine="redis"; node_type="cache.t3.micro"; num_cache_nodes=1; port=6379; security_group_ids=[aws_security_group.redis.id] }

# === Secrets Manager ===
resource "aws_secretsmanager_secret" "db" { name="artispreneur/db" }
resource "aws_secretsmanager_secret_version" "db" {
  secret_id=aws_secretsmanager_secret.db.id
  secret_string=jsonencode({host=aws_db_instance.main.address,port=aws_db_instance.main.port,dbname=var.db_name,username=var.db_username,password=random_password.db.result})
}
