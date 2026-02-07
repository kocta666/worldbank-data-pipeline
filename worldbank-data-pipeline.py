import os
import requests
import json
import boto3
from botocore.exceptions import ClientError
import logging

# --- CONFIGURATION ---
# Читаем из переменных окружения или используем значения по умолчанию
WORLDBANK_API_URL = os.getenv(
    "WORLDBANK_API_URL",
    "https://api.worldbank.org/v2/country/US/indicator/SP.POP.TOTL?format=json"
)
DEFAULT_FILENAME = os.getenv("DEFAULT_FILENAME", "data.json")

# S3/MinIO configuration
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://127.0.0.1:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "api-data")
S3_OBJECT_NAME = os.getenv("S3_OBJECT_NAME", "data.json")
# --- END CONFIGURATION ---

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Логируем конфигурацию (без паролей)
logging.info("Configuration loaded:")
logging.info(f"  WorldBank URL: {WORLDBANK_API_URL}")
logging.info(f"  S3 Endpoint: {S3_ENDPOINT}")
logging.info(f"  S3 Bucket: {S3_BUCKET}")
logging.info(f"  S3 Region: {S3_REGION}")

def fetch_worldbank_data():
    """
        Fetch population data for USA from World Bank API.

        Returns:
            dict or list: JSON response from API

        Raises:
            requests.exceptions.RequestException: If network request fails
        """
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
    """
        save data to file

        Raises:
            IOError
        """
    try:
        logging.info("Saving World Bank Data...")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info("successfully saved World Bank Data")
    except IOError as e:
        logging.error(f"Error saving file: {e}")
        raise

def create_s3_client():
    """
        Initialize and return a configured S3 client.

        Returns:
            An authenticated boto3 S3 client instance.

        Raises:
            ClientError: If AWS authentication or configuration fails.
        """
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
    """
       Upload file to S3 bucket.

       Args:
           s3_client: Initialized S3 client
           bucket: Destination bucket
           filename: Local file path
           object_name: S3 object key

       Raises:
           ClientError: On upload failure
       """
    try:
        logging.info("Uploading to S3 ...")
        s3_client.upload_file(filename, bucket, object_name)
        logging.info("successfully uploaded to S3")
    except ClientError as e:
        logging.error(f"Error uploading to S3 Client: {e}")


def main():
    """
    Main execution flow: fetch World Bank data, save locally, upload to S3.

    Workflow:
    1. Fetch data from World Bank API
    2. Save data to local file
    3. Upload file to S3 bucket

    Exceptions are caught and logged with specific error types.
    """
    try:
        logging.info("Starting World Bank data pipeline...")

        # Step 1: Fetch data
        logging.info("Step 1: Fetching World Bank Data...")
        try:
            data = fetch_worldbank_data()
        except Exception as e:
            logging.error(f"Failed to fetch data from World Bank API: {e}")
            logging.error("Pipeline terminated at data fetching stage")
            return

        # Step 2: Save to file
        logging.info("Step 2: Saving data to local file...")
        try:
            save_to_file(data, DEFAULT_FILENAME)
        except Exception as e:
            logging.error(f"Failed to save data to local file '{DEFAULT_FILENAME}': {e}")
            logging.error("Pipeline terminated at file saving stage")
            return

        # Step 3: Upload to S3
        logging.info("Step 3: Uploading to S3...")
        try:
            s3 = create_s3_client()
        except Exception as e:
            logging.error(f"Failed to create S3 client: {e}")
            logging.error(f"Check S3 configuration: endpoint={S3_ENDPOINT}, bucket={S3_BUCKET}")
            logging.error("Pipeline terminated at S3 client creation")
            return

        try:
            upload_to_s3(
                s3_client=s3,
                bucket=S3_BUCKET,
                filename=DEFAULT_FILENAME,
                object_name=S3_OBJECT_NAME
            )
        except Exception as e:
            logging.error(f"Failed to upload to S3 bucket '{S3_BUCKET}': {e}")
            logging.error(f"File: {DEFAULT_FILENAME}, Object: {S3_OBJECT_NAME}")
            logging.error("Pipeline terminated at S3 upload stage")
            return

        # Success
        logging.info("=" * 50)
        logging.info("SUCCESS: World Bank data pipeline completed")
        logging.info(f"• Data fetched from: {WORLDBANK_API_URL}")
        logging.info(f"• Local file: {DEFAULT_FILENAME}")
        logging.info(f"• S3 location: s3://{S3_BUCKET}/{S3_OBJECT_NAME}")
        logging.info("=" * 50)

    except KeyboardInterrupt:
        logging.warning("Pipeline interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error in main pipeline: {e}", exc_info=True)
        logging.error(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main()

