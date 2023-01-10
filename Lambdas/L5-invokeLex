import json
import random
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    
    logger.debug('input from client={}'.format(event))
    
    data = json.loads(event['body'])
    client_input = data['messages'][0]['unstructured']['text']
    
    logger.debug('client input={}'.format(client_input))
    

    client = boto3.client('lex-runtime')

    lex_response = client.post_text(
        botName='crimeAnalysis',
        botAlias='crimeAnalysisAlias',
        userId="001",
        sessionAttributes={},
        requestAttributes={},
        inputText= client_input
    )
    
    
    logger.debug('lex response={}'.format(lex_response))
    
    lex_output = lex_response["message"]
    
    logger.debug('lex output={}'.format(lex_output))
    message_string = {
                "messages": [
                    {
                        "type": "unstructured",
                        "unstructured": {
                            "id": "string",
                            "text": lex_response['message'],
                            "timestamp": "string"
                        }
                    }
                ]
            }
    return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    },
    'body': json.dumps(message_string)
    }
        
    # return {
    #     'headers': {
    #         'Access-Control-Allow-Headers' : 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    #         'Access-Control-Allow-Origin': '*',
    #         'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    #         },           
    #     'statusCode': 200,
    #     'messages': [{
    #         "type":'unstructured',
    #         "unstructured":{
    #                 'text': lex_output
    #             }
    #         }]
    #     }
