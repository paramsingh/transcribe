import boto3


class WhisperSQSPublisher:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queue_url = 'https://sqs.us-east-1.amazonaws.com/721156031936/whisper-output-queue'
    
    def publish(self, link, text):
        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            DelaySeconds=10,
            MessageAttributes={
                'Video': {
                    'Link': link
                },
            }
            MessageBody=(text)
        )
        print(f"Published response for {link}: {response['MessageId']}")


class WhisperSQSConsumer:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queue_url = 'https://sqs.us-east-1.amazonaws.com/721156031936/whisper-input-queue'

    # Receive message from SQS queue
    def consume(self):
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        if not len(response['Messages']): 
            return None, None

        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        return message, receipt_handle

    # Delete received message from queue
    def delete_message(self, receipt_handle: str):
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % receipt_handle)
