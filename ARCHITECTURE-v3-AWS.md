# Artispreneur v3 — AWS-Native Architecture

## Stack

| Service | AWS Product | Replaces |
|---------|------------|----------|
| Auth | Cognito User Pools | Supabase Auth |
| Database | RDS PostgreSQL + pgvector | Supabase DB |
| Storage | S3 + CloudFront | Supabase Storage |
| API | API Gateway + Lambda (FastAPI) | — |
| LLM | Bedrock DeepSeek V3 | Gemini / BYOK |
| Cache | ElastiCache Redis | — |
| Secrets | Secrets Manager | — |
| CDN | CloudFront | Vercel CDN |
| IaC | Terraform | — |

## Database Schema (RDS PostgreSQL + pgvector)

Core tables: workspace_users, agent_sessions, agent_actions, soul_docs, music_catalog (with vector embeddings), outputs (S3 references), contacts.

Full schema in `terraform/schema.sql`.

## S3 Buckets

| Bucket | Purpose |
|--------|---------|
| artispreneur-static | Frontend (CloudFront CDN) |
| artispreneur-outputs | User files (EPKs, contracts) — 90d IA, 365d Glacier |

## Bedrock DeepSeek V3

- Model: `deepseek.deepseek-v3`
- On-demand pricing: ~$0.50/M tokens
- Used for all agent chat + reasoning
- Streaming support for real-time responses
- Region: us-east-1

## API Endpoints (Lambda + API Gateway)

| Method | Path | Auth |
|--------|------|------|
| POST | /auth/signup | Public |
| POST | /auth/login | Public |
| POST | /agent/chat | JWT |
| GET | /agent/status | JWT |
| GET/POST | /outputs | JWT |
| GET | /directory | Public |

## Deployment

```bash
cd terraform
terraform init
terraform plan
terraform apply
# Deploy frontend to S3
aws s3 sync ../frontend/ s3://artispreneur-static-dev/
# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id $CF_ID --paths "/*"
```

## Monthly Cost (~free tier)
~$1.62/month for dev environment
