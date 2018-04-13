import boto3


class S3DAO:
    '''
    Object to interact with AWS S3
    '''
    def __init__(self, access_key, secret_key):
        self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )

    def download_file_from_s3(self, bucket, file_path, file_name):
        try:
            self.s3_client.download_file(bucket, file_path, file_name)
        except Exception as e:
            raise(e)

    def upload_file_to_s3(self, file, bucket_name, file_path):
        '''
        Uploads a file to S3
        Params:
            file: The file to upload
            bucket_name: The bucket to upload the file to
        '''
        try:
            self.s3_client.upload_fileobj(
                    file,
                    bucket_name,
                    file_path
            )
        except Exception as e:
            raise(e)

    def delete_file_in_s3(self, bucket_name, file_path):
        print(file_path)
        try:
            self.s3_client.delete_object(
                Bucket=bucket_name,
                Key=file_path
            )
        except Exception as e:
            raise(e)
