import boto3

from app.configs.settings import get_settings


def create_storage_client():
    settings = get_settings()
    if (
        not settings.storage_key.get_secret_value()
        or not settings.storage_secret.get_secret_value()
    ):
        raise ValueError("Configure STORAGE_KEY and STORAGE_SECRET before using storage")
    return boto3.client(
        "s3",
        region_name=settings.storage_region,
        aws_access_key_id=settings.storage_key.get_secret_value(),
        aws_secret_access_key=settings.storage_secret.get_secret_value(),
    )
