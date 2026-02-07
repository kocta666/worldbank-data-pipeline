import requests
import json
import boto3

def fetch_worldbank_data():
    url = "https://api.worldbank.org/v2/country/US/indicator/SP.POP.TOTL?format=json"
    response = requests.get(url) # дергаем API
    response.raise_for_status() # упадет если 4хх/5хх
    return response.json() # получаем python-объект (list/dict)


def save_to_file(data, filename="data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_s3_client():
    return boto3.client("s3",
                        endpoint_url="http://127.0.0.1:9000",
                        aws_access_key_id="minioadmin",
                        aws_secret_access_key="minioadmin",
                        region_name="us-east-1",
                        )

def upload_to_s3(s3_client, bucket, filename, object_name):
    s3_client.upload_file(filename, bucket, object_name)


def main():
    data = fetch_worldbank_data()
    save_to_file(data, "data.json")

    s3 = create_s3_client()
    upload_to_s3(
        s3_client=s3,
        bucket="api-data",
        filename="data.json",
        object_name="data.json"
    )

if __name__ == "__main__":
    main()

