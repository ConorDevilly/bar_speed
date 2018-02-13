import boto3
from pprint import pprint
import json

QUEUE_NAME = 'bar_speed_vid_q'
QUEUE_URL = 'https://sqs.eu-west-1.amazonaws.com/804666760197/bar_speed_vid_q'

def main():
	sqs_client = boto3.client('sqs')

	response = sqs_client.receive_message(
				QueueUrl = QUEUE_URL,
				MaxNumberOfMessages = 1,
				WaitTimeSeconds = 10
			)

	vid_path = parse_message_body(response)
	print(vid_path)

# TODO: Get length & go through each
# TODO: Backup for empty messages
# TODO: Deal with new user registrations (i.e: a videos/<num> folder being created)
def parse_message_body(response):
	vid_path = ''
	try:
		msg_body = response['Messages'][0]['Body']
		msg_body = json.loads(response['Messages'][0]['Body'])
		vid_path = msg_body['Records'][0]['s3']['object']['key']
	except KeyError:
		# TODO
		raise
	return vid_path


if __name__ == '__main__':
	main()
