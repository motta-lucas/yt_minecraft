from __future__ import annotations

import json
import os
from datetime import date

import boto3
from botocore.client import Config


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",  # MinIO ignora, mas boto3 exige
    )


def ensure_bucket(client, bucket: str):
    existing = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
    if bucket not in existing:
        client.create_bucket(Bucket=bucket)


def save_to_minio(
    data: list[dict],
    data_origin: str,
    bucket: str | None = None,
):
    client = get_minio_client()
    bucket = bucket or os.environ["MINIO_BUCKET"]

    ensure_bucket(client, bucket)

    today = date.today().isoformat()
    key = f"{data_origin}/dt={today}/{data_origin}.json"

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    return f"s3://{bucket}/{key}"
