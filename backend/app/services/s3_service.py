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
            region_name=os.getenv('AWS_REGION', 'us-east-2')
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
            str: The file name (not URL since we'll generate signed URLs on demand)
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
            
            # Return just the file name, not a URL
            return file_name
            
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
    
    def get_signed_url(self, file_name: str, expiration: int = 3600) -> str:
        """
        Generate a signed URL for secure file access.
        
        Args:
            file_name: The name of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: The signed URL for the file
        """
        try:
            print(f"Generating signed URL for: {file_name}")
            print(f"Bucket: {self.bucket_name}")
            print(f"Region: {os.getenv('AWS_REGION', 'us-east-2')}")
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_name
                },
                ExpiresIn=expiration
            )
            print(f"Generated URL: {url}")
            return url
        except ClientError as e:
            print(f"Error generating signed URL: {e}")
            print(f"Error code: {e.response['Error']['Code']}")
            print(f"Error message: {e.response['Error']['Message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate file access URL"
            )
    
    def get_file_url(self, file_name: str) -> str:
        """
        Get a signed URL for a file (alias for get_signed_url for backward compatibility).
        
        Args:
            file_name: The name of the file
            
        Returns:
            str: The signed URL of the file
        """
        return self.get_signed_url(file_name)

# Create a global instance
s3_service = S3Service() 