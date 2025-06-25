"""
S3 service for handling file operations with AWS S3.
"""

import boto3
import os
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    def upload_file(self, file_data: bytes, file_name: str, content_type: str = None) -> str:
        """
        Upload a file to S3.
        
        Args:
            file_data: The file content as bytes
            file_name: The name to give the file in S3
            content_type: The MIME type of the file
            
        Returns:
            str: The public URL of the uploaded file
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_data,
                **extra_args
            )
            
            # Return the public URL
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
            
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to S3"
            )
    
    def delete_file(self, file_name: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_name: The name of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
    
    def get_file_url(self, file_name: str) -> str:
        """
        Get the public URL for a file.
        
        Args:
            file_name: The name of the file
            
        Returns:
            str: The public URL of the file
        """
        return f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"

# Create a global instance
s3_service = S3Service() 