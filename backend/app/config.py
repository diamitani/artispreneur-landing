"""Frozen config — reads from environment at startup."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    bedrock_model: str = os.getenv("BEDROCK_MODEL", "deepseek.deepseek-v3")
    s3_outputs: str = os.getenv("S3_OUTPUTS", "")
    cognito_client: str = os.getenv("COGNITO_CLIENT", "")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_name: str = os.getenv("DB_NAME", "artispreneur")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_pass: str = os.getenv("DB_PASSWORD", "")


config = Config()
