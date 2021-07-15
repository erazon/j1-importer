import boto3 as boto3

from config import Config


def get_s3_client():
    s3_client = boto3.resource(
        's3',
        aws_access_key_id=Config.ACCESS_KEY,
        aws_secret_access_key=Config.SECRET_KEY
    )
    return s3_client


def get_aws_resources():
    return Config.S3_BUCKET, Config.S3_FOLDER
