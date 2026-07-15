variable "aws_region" { type=string; default="us-east-1" }
variable "environment" { type=string; default="dev" }
variable "db_name" { type=string; default="artispreneur" }
variable "db_username" { type=string; default="artispreneur_admin"; sensitive=true }
variable "db_instance_class" { type=string; default="db.t4g.micro" }

output "api_endpoint" { value=aws_apigatewayv2_api.main.api_endpoint }
output "cloudfront_domain" { value=aws_cloudfront_distribution.main.domain_name }
output "rds_endpoint" { value=aws_db_instance.main.address }
output "cognito_pool_id" { value=aws_cognito_user_pool.main.id }
output "cognito_client_id" { value=aws_cognito_user_pool_client.main.id }
output "s3_static_bucket" { value=aws_s3_bucket.static.id }
output "s3_outputs_bucket" { value=aws_s3_bucket.outputs.id }
output "redis_endpoint" { value=aws_elasticache_cluster.main.cache_nodes[0].address }
output "db_password" { value=random_password.db.result; sensitive=true }
