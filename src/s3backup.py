import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from googlemediaitem import GoogleMediaItem

class S3Backup:
    def __init__(self, bucket: str, key_prefix: str, s3_client: boto3.client):
        self.bucket = bucket
        self.key_prefix = key_prefix
        self.s3_client = s3_client
        self.existing_media_items = set()
        self._load_manifest()

    def _load_manifest(self):
        try:
            # Define the key for the manifest file
            manifest_key = f'{self.key_prefix}/manifest'

            # Get the manifest file from S3
            response = self.s3_client.get_object(Bucket=self.bucket, Key=manifest_key)
            manifest_content = response['Body'].read().decode('utf-8')

            # Parse the manifest content into a set
            self.existing_media_items = set(manifest_content.splitlines())

        except ClientError as e:
            # Handle specific error codes, such as missing file
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"Manifest file not found in bucket '{self.bucket}' with key '{self.key_prefix}/manifest'")
            else:
                print(f"Unexpected error: {e}")

    def upload(self, item: GoogleMediaItem):

        item_id = item.id

        timestamp = item.creation_date.isoformat(timespec='seconds')

        file_name = f'{timestamp}-{item.name}'

        key = f'{self.key_prefix}/{item.creation_date.year:04}/{item.creation_date.month:02}/{file_name}'

        response = self.s3_client.create_multipart_upload(Bucket=self.bucket, Key=key)
        upload_id = response['UploadId']
        part_number = 1
        parts = []

        for chunk in item.download():
            print(f"   Uploading chunk with size {len(chunk)}...")

            part_response = self.s3_client.upload_part(
                Bucket=self.bucket,
                Key=key,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=chunk
            )
            parts.append({
                'ETag': part_response['ETag'],
                'PartNumber': part_number
            })
            part_number += 1

        self.s3_client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )

        self.existing_media_items.add(item_id)






