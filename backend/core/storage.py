import os
import boto3
import io
import logging
from botocore.exceptions import ClientError
from backend.core.hyper_config import config

logger = logging.getLogger(__name__)

# Basic S3-compatible configuration. Can point to AWS S3, Cloudflare R2, MinIO, etc.
S3_ENDPOINT = os.getenv("S3_ENDPOINT", None)   # e.g. "https://<account_id>.r2.cloudflarestorage.com"
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "local_key")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "local_secret")
S3_BUCKET = config.S3_BUCKET

try:
    s3_client = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )
    s3_available = True
except Exception as e:
    logger.error(f"Failed to initialize Boto3 S3 Client: {e}")
    s3_available = False

def upload_base64_result(job_id: str, user_id: str, base64_data: str, extension: str = "png") -> str:
    """
    Submits an AI-generated image or heavy string out to S3.
    Returns the URL/Key location.
    """
    if not s3_available:
        return f"mock_storage://{user_id}/{job_id}.{extension}"
        
    import base64
    try:
        binary_data = base64.b64decode(base64_data)
        file_key = f"{user_id}/{job_id}/result.{extension}"
        
        # Uploading to the bucket
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file_key,
            Body=binary_data,
            ContentType=f"image/{extension.replace('jpg', 'jpeg')}" if extension in ['png', 'jpg', 'jpeg'] else "application/json"
        )
        
        # Generate Presigned URL valid for 24 hours
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': file_key},
            ExpiresIn=86400
        )
        return url
        
    except ClientError as e:
        logger.error(f"Failed writing Object Storage to {S3_BUCKET}: {e}")
        return base64_data # Fallback to simply returning raw data to Redis
        
    except Exception as e:
        logger.error(f"Storage Error: {e}")
        return base64_data
