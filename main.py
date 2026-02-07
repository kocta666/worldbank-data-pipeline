import requests
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging

# CONSTANTS
WORLDBANK_API_URL = "https://api.worldbank.org/v2/country/US/indicator/SP.POP.TOTL?format=json"
DEFAULT_FILENAME = "data.json"
S3_ENDPOINT = "http://127.0.0.1:9000"
S3_ACCESS_KEY = "minioadmin"
S3_SECRET_KEY = "minioadmin"
S3_REGION = "us-east-1"
S3_BUCKET = "api-data"
S3_OBJECT_NAME = "data.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def fetch_worldbank_data():
    try:
        logging.info("Fetching World Bank Data...")
        url = WORLDBANK_API_URL
        response = requests.get(url) # дергаем API
        response.raise_for_status() # упадет если 4хх/5хх
        logging.info("successfully fetched World Bank Data")
        return response.json() # получаем python-объект (list/dict)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching World Bank Data: {e}")
        raise # Пробрасываем дальше, если можно вернуть None


def save_to_file(data, filename=DEFAULT_FILENAME):
    try:
        logging.info("Saving World Bank Data...")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info("successfully saved World Bank Data")
    except IOError as e:
        logging.error(f"Error saving file: {e}")
        raise

def create_s3_client():
    try:
        logging.info("Creating S3 Client ...")
        return boto3.client("s3",
                        endpoint_url=S3_ENDPOINT,
                        aws_access_key_id=S3_ACCESS_KEY,
                        aws_secret_access_key=S3_SECRET_KEY,
                        region_name=S3_REGION,
                        )
    except ClientError as e:
        logging.error(f"Error creating S3 Client: {e}")
        raise

def upload_to_s3(s3_client, bucket, filename, object_name):
    try:
        logging.info("Uploading to S3 ...")
        s3_client.upload_file(filename, bucket, object_name)
        logging.info("successfully uploaded to S3")
    except ClientError as e:
        logging.error(f"Error uploading to S3 Client: {e}")

def main():
    try:
        logging.info("Fetching World Bank Data...")
        data = fetch_worldbank_data()
        save_to_file(data, DEFAULT_FILENAME)

        s3 = create_s3_client()
        upload_to_s3(
            s3_client=s3,
            bucket=S3_BUCKET,
            filename=DEFAULT_FILENAME,
            object_name=S3_OBJECT_NAME
        )
        logging.info("Successfully saved World Bank Data")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()

