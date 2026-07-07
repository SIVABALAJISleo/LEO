#!/usr/bin/env python3
"""
Project HYPER - Nightly Database & State Backup Script
Automates snapshotting of the internal SQL/NoSQL structures and syncs to S3.
"""
import os
import tarfile
from datetime import datetime
import logging

try:
    import boto3
except ImportError:
    boto3 = None

logging.basicConfig(level=logging.INFO)

BACKUP_DIR = "backups"
DB_FILE = "hyper_engine.db"
S3_BUCKET = os.getenv("HYPER_BACKUPS_BUCKET", "hyper-saas-backups")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

def run_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    tar_name = f"hyper_backup_{timestamp}.tar.gz"
    tar_path = os.path.join(BACKUP_DIR, tar_name)
    
    # 1. Archive Databases
    logging.info(f"Creating local archive: {tar_path}")
    with tarfile.open(tar_path, "w:gz") as tar:
        if os.path.exists(DB_FILE):
            tar.add(DB_FILE)
            logging.info(f"-> Archived {DB_FILE}")
        
    # 2. Upload to Object Storage (S3 / R2)
    s3_key = os.getenv("AWS_ACCESS_KEY_ID")
    if boto3 and s3_key:
        try:
            s3 = boto3.client('s3', region_name=AWS_REGION)
            s3.upload_file(tar_path, S3_BUCKET, tar_name)
            logging.info(f"Successfully uploaded {tar_name} to s3://{S3_BUCKET}")
        except Exception as e:
            logging.error(f"S3 Upload Failed: {e}")
    else:
        logging.warning("S3 credentials or boto3 not configured. Local backup only.")

if __name__ == "__main__":
    run_backup()
