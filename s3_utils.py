import boto3
from botocore.exceptions import NoCredentialsError
import uuid
from typing import Optional


class s3Uploader:
    def __init__(self, 
                 bucket_name:str, 
                 aws_access_key_id:str, 
                 aws_secret_access_key:str):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket_name = bucket_name
    
    def upload_file(self, file, file_type:str):

        try:
            filename = f"{file_type}_image_{uuid.uuid4()}.{file.filename.split('.')[-1]}"

            self.s3_client.upload_fileobj(
                file.file, 
                self.bucket_name, 
                filename, 
                ExtraArgs={'ContentType': file.content_type}
            )

            return f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
        
        except NoCredentialsError:
            print('No credentials were available')
            return None
        except Exception as e:
            print(f"Error uploading file to s3: {e}")
            return None