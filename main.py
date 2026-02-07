import requests
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# CONSTANTS
WORLDBANK_API_URL = "https://api.worldbank.org/v2/country/US/indicator/SP.POP.TOTL?format=json"
DEFAULT_FILENAME = "data.json"
S3_ENDPOINT = "http://127.0.0.1:9000"
S3_ACCESS_KEY = "minioadmin"
S3_SECRET_KEY = "minioadmin"
S3_REGION = "us-east-1"
S3_BUCKET = "api-data"
S3_OBJECT_NAME = "data.json"

def fetch_worldbank_data():
    try:
        url = WORLDBANK_API_URL
        response = requests.get(url) # дергаем API
        response.raise_for_status() # упадет если 4хх/5хх
        return response.json() # получаем python-объект (list/dict)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к WorldBank API: {e}")
        raise # Пробрасываем дальше, если можно вернуть None


def save_to_file(data, filename=DEFAULT_FILENAME):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка при записи файла {filename}: {e}")
        raise

def create_s3_client():
    try:
        return boto3.client("s3",
                        endpoint_url=S3_ENDPOINT,
                        aws_access_key_id=S3_ACCESS_KEY,
                        aws_secret_access_key=S3_SECRET_KEY,
                        region_name=S3_REGION,
                        )
    except ClientError as e:
        print(f"Ошибка доступа к S3: {e}")
        raise

def upload_to_s3(s3_client, bucket, filename, object_name):
    try:
        s3_client.upload_file(filename, bucket, object_name)
    except ClientError as e:
        print(f"Ошибка доступа к S3: {e}")

def main():
    try:
        data = fetch_worldbank_data()
        save_to_file(data, DEFAULT_FILENAME)

        s3 = create_s3_client()
        upload_to_s3(
            s3_client=s3,
            bucket=S3_BUCKET,
            filename=DEFAULT_FILENAME,
            object_name=S3_OBJECT_NAME
        )
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()

