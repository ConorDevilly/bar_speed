import boto3
import sys


BUCKET_NAME = 'barspeedvids'


def main():
    s3_client = boto3.client('s3')

    key = ''
    for line in sys.stdin:
            key = line.strip()

    s3_client.download_file(BUCKET_NAME, key, 'test.mp4')


if __name__ == '__main__':
    main()
