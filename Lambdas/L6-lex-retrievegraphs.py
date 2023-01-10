#Test event 
#{'messageVersion': '1.0', 'invocationSource': 'FulfillmentCodeHook', 'userId': 'qs10mc2mgd8r0j9tmmbmnhtf5wxfo9bk', 'sessionAttributes': {}, 'requestAttributes': None, 'bot': {'name': 'graphAnalytics', 'alias': '$LATEST', 'version': '$LATEST'}, 'outputDialogMode': 'Text', 'currentIntent': {'name': 'graph_kind_of_crime', 'slots': {'fromDate': '2015-12-31', 'endDate': '2015-12-31', 'place': 'manhattan'}, 'slotDetails': {'fromDate': {'resolutions': [{'value': '2015-12-31'}], 'originalValue': '31 dec 2015'}, 'endDate': {'resolutions': [{'value': '2015-12-31'}], 'originalValue': '31 dec 2015'}, 'place': {'resolutions': [], 'originalValue': 'manhattan'}}, 'confirmationStatus': 'None', 'nluIntentConfidenceScore': 1.0}, 'alternativeIntents': [{'name': 'AMAZON.FallbackIntent', 'slots': {}, 'slotDetails': {}, 'confirmationStatus': 'None', 'nluIntentConfidenceScore': None}, {'name': 'graph_crime_trend', 'slots': {'fromDate': None, 'endDate': '2015-12-31', 'place': None, 'crimeType': None}, 'slotDetails': {'fromDate': None, 'endDate': {'resolutions': [{'value': '2015-12-31'}], 'originalValue': '31 dec 2015'}, 'place': None, 'crimeType': None}, 'confirmationStatus': 'None', 'nluIntentConfidenceScore': 0.44}, {'name': 'graph_safe_city', 'slots': {'fromDate': None, 'endDate': '2015-12-31'}, 'slotDetails': {'fromDate': None, 'endDate': {'resolutions': [{'value': '2015-12-31'}], 'originalValue': '31 dec 2015'}}, 'confirmationStatus': 'None', 'nluIntentConfidenceScore': 0.43}], 'inputTranscript': '31 dec 2015', 'recentIntentSummaryView': [{'intentName': 'graph_kind_of_crime', 'checkpointLabel': None, 'slots': {'fromDate': '2015-12-31', 'endDate': None, 'place': 'manhattan'}, 'confirmationStatus': 'None', 'dialogActionType': 'ElicitSlot', 'fulfillmentState': None, 'slotToElicit': 'endDate'}], 'sentimentResponse': None, 'kendraResponse': None}

import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import decimal 
import boto3
import requests
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import datetime

endpoint = 'https://cloudproj-xxxxxx.es.us-east-1.aws.found.io/'

index = 'violence6/'
op = '_search'
headers = {"Content-Type": "application/json"}
auth=('xxxxxxx', 'xxxxxxxxxxxxxx')

s3 = boto3.client('s3')

location_types = ['manhattan', 'brooklyn', 'queens', 'staten island', 'bronx']
crime_types = ['FORGERY', 'MURDER & NON-NEGL. MANSLAUGHTER', 'DANGEROUS DRUGS',
       'ASSAULT 3 & RELATED OFFENSES', 'FELONY ASSAULT',
       'DANGEROUS WEAPONS', 'PETIT LARCENY', 'GRAND LARCENY', 'ROBBERY',
       'OFFENSES AGAINST PUBLIC ADMINI', 'CRIMINAL MISCHIEF & RELATED OF',
       'RAPE', 'INTOXICATED & IMPAIRED DRIVING', 'HARRASSMENT 2',
       'SEX CRIMES', 'BURGLARY', 'CRIMINAL TRESPASS',
       'MISCELLANEOUS PENAL LAW', 'VEHICLE AND TRAFFIC LAWS',
       'OFF. AGNST PUB ORD SENSBLTY &', 'FRAUDS',
       'GRAND LARCENY OF MOTOR VEHICLE', 'OFFENSES INVOLVING FRAUD',
       'OFFENSES AGAINST THE PERSON', 'FRAUDULENT ACCOSTING',
       'OTHER OFFENSES RELATED TO THEF', 'GAMBLING', 'ARSON',
       'POSSESSION OF STOLEN PROPERTY', 'UNAUTHORIZED USE OF A VEHICLE',
       'THEFT-FRAUD', 'DISORDERLY CONDUCT', '', 'ADMINISTRATIVE CODE',
       'CHILD ABANDONMENT/NON SUPPORT', 'OTHER STATE LAWS (NON PENAL LA',
       'NYS LAWS-UNCLASSIFIED FELONY', "BURGLAR'S TOOLS",
       'THEFT OF SERVICES', 'PETIT LARCENY OF MOTOR VEHICLE',
       'ALCOHOLIC BEVERAGE CONTROL LAW',
       'AGRICULTURE & MRKTS LAW-UNCLASSIFIED', 'ENDAN WELFARE INCOMP',
       'KIDNAPPING & RELATED OFFENSES', 'DISRUPTION OF A RELIGIOUS SERV',
       'PROSTITUTION & RELATED OFFENSES', 'JOSTLING',
       'ANTICIPATORY OFFENSES', 'NYS LAWS-UNCLASSIFIED VIOLATION',
       'HOMICIDE-NEGLIGENT-VEHICLE', 'OFFENSES AGAINST PUBLIC SAFETY',
       'OTHER STATE LAWS', 'ESCAPE 3', 'OFFENSES RELATED TO CHILDREN',
       'UNLAWFUL POSS. WEAP. ON SCHOOL', 'ADMINISTRATIVE CODES',
       'NEW YORK CITY HEALTH CODE', 'LOITERING/GAMBLING (CARDS, DIC',
       'ABORTION', 'KIDNAPPING AND RELATED OFFENSES', 'LOITERING',
       'OTHER STATE LAWS (NON PENAL LAW)', 'INTOXICATED/IMPAIRED DRIVING',
       'FORTUNE TELLING', 'KIDNAPPING', 'UNDER THE INFLUENCE OF DRUGS',
       'OTHER TRAFFIC INFRACTION', 'HOMICIDE-NEGLIGENT,UNCLASSIFIE',
       'LOITERING FOR DRUG PURPOSES']

logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

def elicit_slot(intent_name, slots, slot_to_elicit, message):
    return {
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def close(fulfillment_state, message):
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def delegate(slots):
    return {
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


        
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
    
def validate_params(location, fromDate, endDate, crimeType):
    
    # validate that location is from list                                  
    if location is not None:
        if location.lower() not in location_types:
            return build_validation_result(False,
                                       'place',
                                       'We dont monitor {} location, Please try a different place'.format(location))
    
    # validate that crime type is from list                                  
    if crimeType is not None:
        if crimeType.upper() not in crime_types:
            return build_validation_result(False,
                                       'crimeType',
                                       'We dont monitor {} crime type, Please try a different type'.format(crimeType))
    
    # validate Date: from date should be past or today
    if fromDate:
        user_date1 = datetime.datetime.strptime(fromDate, '%Y-%m-%d').date()
        curr_date = datetime.date.today()
        
        if not isvalid_date(fromDate):
            return build_validation_result(False, 'fromDate', 'Sorry, the start date is not valid. Please enter a valid start date')
            

        elif user_date1 > curr_date:
            return build_validation_result(False, 'fromDate', 'Sorry, the start date is in the future. Can you try a different start date?')
    
    # validate Date: end date should be past or today
    if endDate:
        user_date2 = datetime.datetime.strptime(endDate, '%Y-%m-%d').date()
        curr_date = datetime.date.today()
        
        if not isvalid_date(endDate):
            return build_validation_result(False, 'endDate', 'Sorry, the end date is not valid. Please enter a valid end date')
            

        elif (user_date2 > curr_date) or (user_date2 < user_date1):
            return build_validation_result(False, 'endDate', 'Sorry, the end date is in the future or before chosen start date. Can you try a different end date?')
    

    return build_validation_result(True, None, None)

#Plot graph and store in S3
def plot_store(x, y, xlabel, ylabel, title, graphName):

    print(type(x))
    print(type(y))

    #Plot
    img_data = BytesIO()
    #fig = plt.figure(figsize = (10, 5))
    
    # creating the bar plot
    fig, ax = plt.subplots()

    fig.set_size_inches(18.5, 10.5, forward=True)
    ax.bar(x, y, color = ['red', 'yellow', 'green', 'blue', 'orange'], width = 0.4)
    fig.autofmt_xdate()

    ax.set_xlabel(xlabel, fontsize=18)
    ax.set_ylabel(ylabel, fontsize=18)

    ax.set_title(title, fontsize=22)

    for i, v in enumerate(y):
        ax.text(i, v+0.5,  str(v),color = 'blue', fontweight = 'bold')

    plt.savefig(img_data, format='png')
    img_data.seek(0)

    #Store in S3 and get url
    out_bucket = 'crime-graphs'
    ct = str(datetime.datetime.now())
    ct_split = ct.split()
    ct = ct_split[0] + 'T' + ct_split[1]
    out_key = graphName + ct + ".png"

    # put plot in S3 bucket
    bucket = boto3.resource('s3').Bucket(out_bucket)
    bucket.put_object(Body=img_data, ContentType='image/png', Key=out_key)

    url = "https://crime-graphs.s3.amazonaws.com/" + out_key
    
    return url

    





#Handle graph_kind_of_crime intent
def graph_kind_of_crime(intent_request):
    
    source = intent_request['invocationSource']
    place = intent_request['currentIntent']['slots']['place']
    fromDate = intent_request['currentIntent']['slots']['fromDate']
    endDate = intent_request['currentIntent']['slots']['endDate']
    
    if source == 'FulfillmentCodeHook':  
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_params(place, fromDate, endDate, None)
        
        # if any slot is invalid
        if not validation_result['isValid']:
            x = validation_result['violatedSlot']
            print(str(x) + "is invalid")
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        # Get the data from ES, plot graph, store in S3, return link
        else:
            fromDate = str(fromDate) + "T00:00:00" 
            endDate = str(endDate)

            date_1 = datetime.datetime.strptime(endDate, "%Y-%m-%d")

            end_date_new = date_1 + datetime.timedelta(days=1)

            
            temp_date = str(end_date_new).split()
            end_date_new = temp_date[0] + "T" + temp_date[1]
 
            query = {
                    "aggs": {
                        "categories": {            
                        "filter": {
                            "bool" : {
                            "must" : [
                                {"term": {"location.keyword": place.upper()}}
                                ],
                            "filter": {
                                "range": {
                                    "date": {
                                        "gte": fromDate,
                                        "lte": end_date_new
                                    }
                                }
                            }
                            }
                        },
                        "aggs": {
                            "names": {
                            "terms": {"field": "crimeType.keyword", "size": 5}
                            }
                        }
                        }
                    }
                }
            url = endpoint + index + op
            res = json.loads(requests.get(url, headers=headers, auth = auth, data=json.dumps(query)).text)
            
            result = res["aggregations"]["categories"]["names"]["buckets"]

            if(len(result) == 0):
                return close(
                    'Fulfilled',
                    {
                        'contentType': 'PlainText',
                        'content': 'No crimes were recorded on the given set of values'
                    }
                )

            x = []
            y = []

            for ele in result:
                x.append(ele['key'])
                y.append(ele['doc_count'])

            url = plot_store(x, y, "Crime Type", "Crime Count", "Plot of Crime Type vs Crime Count", "graph_kind_of_crime")
    
    return close(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Please find the graph here: ' + str(url)
        }
    )

#Handle graph_crime_trend intent
def graph_crime_trend(intent_request):
    
    source = intent_request['invocationSource']
    place = intent_request['currentIntent']['slots']['place']
    fromDate = intent_request['currentIntent']['slots']['fromYear']
    endDate = intent_request['currentIntent']['slots']['endYear']

    fromDate = str(fromDate)+"-01-01"
    if (str(endDate) == "2022"):
        #then enddate should be todays current date
        end_date_temp = str(datetime.datetime.strptime(str(datetime.date.today()), "%Y-%m-%d"))
        temp_date = str(end_date_temp).split()
        endDate = temp_date[0]
    else:
        endDate = str(endDate)+"-12-31"
    
    if source == 'FulfillmentCodeHook':  
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_params(place, fromDate, endDate, None)
        
        # if any slot is invalid
        if not validation_result['isValid']:
            x = validation_result['violatedSlot']
            print(str(x) + "is invalid")
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        
        # Get the data from ES, plot graph, store in S3, return link
        else:
            fromDate = str(fromDate) + "T00:00:00" 
            endDate = str(endDate)

            date_1 = datetime.datetime.strptime(endDate, "%Y-%m-%d")

            end_date_new = date_1 + datetime.timedelta(days=1)

            
            temp_date = str(end_date_new).split()
            end_date_new = temp_date[0] + "T" + temp_date[1]
 
            query = {
                    "aggs": {
                        "categories": {            
                            "filter": {
                                "bool" : {
                                "must" : [
                                    {"term": {"location.keyword": place.upper()}}
                                    ],
                                "filter": {
                                    "range": {
                                        "date": {
                                            "gte": fromDate,
                                            "lte": end_date_new
                                        }
                                    }
                                }
                                }
                            },
                            "aggs": {
                                "names": {
                                    "date_histogram": {
                                        "field": "date",
                                        "calendar_interval": "1y"
                                    }
                                }
                            }
                        }
                    }
                }
            url = endpoint + index + op
            res = json.loads(requests.get(url, headers=headers, auth = auth, data=json.dumps(query)).text)
                #crime_count.append(int(res['count']))
            
            print(res)
            result = res["aggregations"]["categories"]["names"]["buckets"]

            if(len(result) == 0):
                return close(
                    'Fulfilled',
                    {
                        'contentType': 'PlainText',
                        'content': 'No crimes were recorded on the given set of values'
                    }
                )

            x = []
            y = []

            for ele in result:
                x.append(ele['key_as_string'][0:4])
                y.append(ele['doc_count'])

            url = plot_store(x, y, "Year", "Crime Count", "Plot of Crime Count over years", "graph_crime_trend")

    
    return close(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Please find the graph here: ' + str(url)
        }
    )

#Handle graph_safe_city intent
def graph_safe_city(intent_request):
    
    source = intent_request['invocationSource']
    fromDate = intent_request['currentIntent']['slots']['fromDate']
    endDate = intent_request['currentIntent']['slots']['endDate']
    
    if source == 'FulfillmentCodeHook':  
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_params(None, fromDate, endDate, None)
        
        # if any slot is invalid
        if not validation_result['isValid']:
            x = validation_result['violatedSlot']
            print(str(x) + "is invalid")
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        # Get the data from ES, plot graph, store in S3, return link
        else:
            fromDate = str(fromDate) + "T00:00:00" 
            endDate = str(endDate)

            date_1 = datetime.datetime.strptime(endDate, "%Y-%m-%d")

            end_date_new = date_1 + datetime.timedelta(days=1)

            
            temp_date = str(end_date_new).split()
            end_date_new = temp_date[0] + "T" + temp_date[1]
 
            query = {
                    "aggs": {
                        "categories": {            
                        "filter": {
                            "bool" : {
                            "filter": {
                                "range": {
                                    "date": {
                                        "gte": fromDate,
                                        "lte": end_date_new
                                    }
                                }
                            }
                            }
                        },
                        "aggs": {
                            "names": {
                            "terms": {"field": "location.keyword", "size": 5}
                            }
                        }
                        }
                    }
                }
            url = endpoint + index + op
            res = json.loads(requests.get(url, headers=headers, auth = auth, data=json.dumps(query)).text)
            
            result = res["aggregations"]["categories"]["names"]["buckets"]

            if(len(result) == 0):
                return close(
                    'Fulfilled',
                    {
                        'contentType': 'PlainText',
                        'content': 'No crimes were recorded on the given set of values'
                    }
                )

            x = []
            y = []

            for ele in result:
                x.append(ele['key'])
                y.append(ele['doc_count'])

            url = plot_store(x, y, "Borough", "Crime Count", "Plot of Borough vs Crime Count", "graph_safe_city")

    
    return close(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Please find the graph here: ' + str(url)
        }
    )
    
    
def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    
    if intent_name == 'kind_of_crime':
        return graph_kind_of_crime(intent_request)
    elif intent_name == 'safe_city':
        return graph_safe_city(intent_request)
    elif intent_name == 'crime_trend':
        return graph_crime_trend(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')    

def lambda_handler(event, context):
    print(event)
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    logger.debug('event={}'.format(event))
    response = dispatch(event)
    logger.debug('response={}'.format(response))
    return response  
