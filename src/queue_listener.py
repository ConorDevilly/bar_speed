import boto3
import json
from job_coordinator import JobCoordinator

class QueueListener:
    def __init__(self, queue_url):
        self.sqs_client = boto3.client('sqs')
        self.coordinator = JobCoordinator()
        self.queue_url = queue_url


    def listen(self):
        while(True):
            message = self.sqs_client.receive_message(
                                    QueueUrl = self.queue_url,
                                    MaxNumberOfMessages = 1,
                                    WaitTimeSeconds = 10
                    )
            vid_path = self.parse_msg_body(message)
            if vid_path is not None:
                self.start_coordinator(vid_path)
                self.sqs_client.delete_message(
                            QueueUrl = self.queue_url,
                            ReceiptHandle = message['Messages'][0]['ReceiptHandle']
                        )

    def start_coordinator(self, vid_path):
        self.coordinator.start(vid_path)

    def parse_msg_body(self, msg):
        '''
        Parses an S3 path from an SQS message
        Params:
            msg: The SQS message
        Returns:
            vid_path: string: The parsed message body
        '''
        vid_path = None
        try:
            msg_body = json.loads(msg['Messages'][0]['Body'])
            vid_path = msg_body['Records'][0]['s3']['object']['key']
        except KeyError:
            # Key error means no message were found
            pass
        return vid_path
