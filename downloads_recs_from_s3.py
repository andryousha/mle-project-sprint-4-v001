import boto3
import os
from dotenv import load_dotenv

load_dotenv(override=True)

PATH = 'recsys/data/'

FILES = [
    "top_100_popular.parquet",
    "recommendations.parquet",
    "similar.parquet"
]

DIRECTORY = 'data_recs'


session = boto3.session.Session()

s3_client = session.client(
    service_name='s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url=os.getenv('S3_URL')
)

if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

for file_name in FILES:
    s3_client.download_file(
        Bucket=os.getenv('S3_BUCKET_NAME'),
        Filename=f'{DIRECTORY}/{file_name}',
        Key=PATH + file_name)
