import boto3
import json
import sys
import time



class VideoDetect:
    jobId = ''
    rek = boto3.client('rekognition',region_name="us-east-1", aws_access_key_id='XXXX', aws_secret_access_key='XXXXX')
    sqs = boto3.client('sqs',region_name="us-east-1", aws_access_key_id='XXXXX', aws_secret_access_key='XXXXX')
    sns = boto3.client('sns',region_name="us-east-1", aws_access_key_id='XXXXX', aws_secret_access_key='XXXXX')
    
    roleArn = ''
    bucket = ''
    video = ''
    startJobId = ''

    sqsQueueUrl = ''
    snsTopicArn = ''
    processType = ''

    def __init__(self, role, bucket, video):    
        self.roleArn = role
        self.bucket = bucket
        self.video = video

    def GetSQSMessageSuccess(self):

        jobFound = False
        succeeded = False
    
        dotLine=0
        while jobFound == False:
            sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=10)

            if sqsResponse:
                
                if 'Messages' not in sqsResponse:
                    if dotLine<40:
                        print('.', end='')
                        dotLine=dotLine+1
                    else:
                        print()
                        dotLine=0    
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse['Messages']:
                    notification = json.loads(message['Body'])
                    rekMessage = json.loads(notification['Message'])
                    print(rekMessage['JobId'])
                    print(rekMessage['Status'])
                    if rekMessage['JobId'] == self.startJobId:
                        print('Matching Job Found:' + rekMessage['JobId'])
                        jobFound = True
                        if (rekMessage['Status']=='SUCCEEDED'):
                            succeeded=True
                        else:
                            print(str(rekMessage))    

                        self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                       ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" +
                              str(rekMessage['JobId']) + ' : ' + self.startJobId)
                    # Delete the unknown message. Consider sending to dead letter queue
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                   ReceiptHandle=message['ReceiptHandle'])


        return succeeded

    def StartContentModeration(self):
        response=self.rek.start_content_moderation(Video={'S3Object': {'Bucket': self.bucket, 'Name': self.video}},
            NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn})

        self.startJobId=response['JobId']
        print('Start Job Id: ' + self.startJobId)


    def GetContentModeration(self):
        maxResults = 10
        paginationToken = ''
        finished = False

        while finished == False:
            response = self.rek.get_content_moderation(JobId=self.startJobId,
                                            MaxResults=maxResults,
                                            NextToken=paginationToken,
                                            SortBy='TIMESTAMP')

            print('Codec: ' + response['VideoMetadata']['Codec'])
            print('Duration: ' + str(response['VideoMetadata']['DurationMillis']))
            print('Format: ' + response['VideoMetadata']['Format'])
            print('Frame rate: ' + str(response['VideoMetadata']['FrameRate']))
            print()
            if response['ModerationLabels']==[]:
                print("No violence found")
                break
            else:
                for mod_label in response['ModerationLabels']:
                    label=mod_label['ModerationLabel']
                    print(" The Time stamp  " + str(mod_label['Timestamp']))
                    print(" Parent Label: " + str(label['ParentName']))
                    print("   Label: " + label['Name'])
                    print("   Confidence: " +  str(label['Confidence']))
                    print("   Instances:")
                # for instance in label['Instances']:
                #     print ("      Confidence: " + str(instance['Confidence']))
                #     print ("      Bounding box")
                #     print ("        Top: " + str(instance['BoundingBox']['Top']))
                #     print ("        Left: " + str(instance['BoundingBox']['Left']))
                #     print ("        Width: " +  str(instance['BoundingBox']['Width']))
                #     print ("        Height: " +  str(instance['BoundingBox']['Height']))
                #     print()
                # print()
                # print ("   Parents:")
                # for parent in label['Parents']:
                #     print ("      " + parent['Name'])
                # print ()

                    if 'NextToken' in response:
                        paginationToken = response['NextToken']
                    else:
                        finished = True
       
    
    def CreateTopicandQueue(self):
      
        millis = str(int(round(time.time() * 1000)))

        #Create SNS topic
        
        snsTopicName="AmazonRekognitionExample" + millis

        topicResponse=self.sns.create_topic(Name=snsTopicName)
        self.snsTopicArn = topicResponse['TopicArn']

        #create SQS queue
        sqsQueueName="AmazonRekognitionQueue" + millis
        self.sqs.create_queue(QueueName=sqsQueueName)
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsQueueName)['QueueUrl']
 
        attribs = self.sqs.get_queue_attributes(QueueUrl=self.sqsQueueUrl,
                                                    AttributeNames=['QueueArn'])['Attributes']
                                        
        sqsQueueArn = attribs['QueueArn']

        # Subscribe SQS queue to SNS topic
        self.sns.subscribe(
            TopicArn=self.snsTopicArn,
            Protocol='sqs',
            Endpoint=sqsQueueArn)

        #Authorize SNS to write SQS queue 
        policy = """{{
  "Version":"2012-10-17",
  "Statement":[
    {{
      "Sid":"MyPolicy",
      "Effect":"Allow",
      "Principal" : {{"AWS" : "*"}},
      "Action":"SQS:SendMessage",
      "Resource": "{}",
      "Condition":{{
        "ArnEquals":{{
          "aws:SourceArn": "{}"
        }}
      }}
    }}
  ]
}}""".format(sqsQueueArn, self.snsTopicArn)
 
        response = self.sqs.set_queue_attributes(
            QueueUrl = self.sqsQueueUrl,
            Attributes = {
                'Policy' : policy
            })

    def DeleteTopicandQueue(self):
        self.sqs.delete_queue(QueueUrl=self.sqsQueueUrl)
        self.sns.delete_topic(TopicArn=self.snsTopicArn)


def main():
    roleArn = 'arn:aws:iam::942877294827:role/RecognitionRole'   
    bucket = 'test-bucket-rv2'
    video = 'videos/new_video/Normal2.mp4'

    analyzer=VideoDetect(roleArn, bucket,video)
    analyzer.CreateTopicandQueue()

    analyzer.StartContentModeration()
    if analyzer.GetSQSMessageSuccess()==True:
        print("Coming in")
        analyzer.GetContentModeration()
    
    analyzer.DeleteTopicandQueue()


if __name__ == "__main__":
    main()