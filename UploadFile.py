import boto3
import os
from dotenv import load_dotenv

load_dotenv()

#side note: you can use any S3 API compatible storge provider! I've personally used Cloudflare's R2.

def uploadFileToCloud(filename, prefix):
    b2_file_name = filename

    # Initialize the S3 client
    s3 = boto3.resource(
        "s3",
        endpoint_url=os.getenv("S3COMPAT_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("S3KEYID"),
        aws_secret_access_key=os.getenv("S3SECRET"),
    )

    # Specify the bucket and file
    bucket = s3.Bucket(os.getenv("S3_BUCKET_NAME"))

    with open(filename, "rb") as f:
        res = bucket.Object(prefix+b2_file_name).put(Body=f.read())

    fileURL = os.getenv("S3_BUCKET_PUBLIC_URL")+prefix+b2_file_name

    return(fileURL)

if __name__ == "__main__":
    uploadFileToCloud("test.html","webpage/")