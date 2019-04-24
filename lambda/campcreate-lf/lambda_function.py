from __future__ import print_function

'''
Lambda function to copy message to a destination room and notify sender
'''

import json
import os

from botocore.vendored import requests
import ucsm_operations

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_ID = os.environ['BOT_ID']
DEST_ROOM = os.environ['DEST_ROOM']

SSH_HOST = os.environ['SSH_HOST']
SSH_USER = os.environ['SSH_USER']
SSH_PASS = os.environ['SSH_PASS']

GET_HEADERS = {
    "Authorization": "Bearer %s" % BOT_TOKEN,
    "Accept": "application/json"
}

POST_HEADERS = {
    "Authorization": "Bearer %s" % BOT_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

API_URL = os.environ['API_URL']
MESSAGES = '/messages'
WEBHOOKS = '/webhooks'

print('Loading function')

def respond(err, res=None):
    '''
    Return request status
    '''
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def http_action(http_method, api_url, http_headers, body_data=None):
    '''
    Run specified HTTP Method with Supplied parameters
    '''

    if http_method == 'GET':
        response = requests.get(api_url, headers=http_headers, verify=True)
    elif http_method == 'POST':
        response = requests.post(
            api_url, headers=http_headers, data=json.dumps(body_data), verify=True)

    print(response)

    return response.json()


def process_msg(payload):
    '''
    Get the message
      - Send to Destination Team roomId
      - Send confirmation to sender
    '''

    person_id = payload['data']['personId']
    person_email = payload['data']['personEmail']
    message_id = payload['data']['id']

    print("Message Id")
    print(payload['data']['id'])

    response_body = http_action('GET', API_URL + MESSAGES + "/" + message_id, GET_HEADERS)
    print('Message Get Response')
    print(response_body)

    new_message = response_body['text']
    print(new_message)
    
    ucs_response = "no operation requested"
    if "UCS Get-Inventory" in new_message:
        ucs_response = ucsm_operations.get_ucs_inventory()

    if "UCS Get-Faults" in new_message:
        ucs_response = ucsm_operations.get_ucs_faults()

    if "UCS Get-Users" in new_message:
        ucs_response = ucsm_operations.get_ucs_user()

    if "UCS Add-User" in new_message:
        startIndex = new_message.find("UCS Add-User")
        ucs_response = ucsm_operations.add_ucs_user(new_message[startIndex+13:])

    if "UCS Delete-User" in new_message:
        startIndex = new_message.find("UCS Delete-User")
        ucs_response = ucsm_operations.delete_ucs_user(new_message[startIndex+16:])

    if "UCS Add-Vlan" in new_message:
        startIndex = new_message.find("UCS Add-Vlan")
        inputString = new_message[startIndex+13:]
        inputs = inputString.split(',')
        ucs_response = ucsm_operations.add_ucs_vlan(inputs[0], inputs[1])

    if "help" in new_message:
        print("HELP!")
        ucs_response = ("Possible Operations:<br/>UCS Get-Inventory<br/>UCS Get-Faults<br/>UCS Get-Users<br/>UCS Add-User <first,last,email,username,privilege>"
                        + "<br/>UCS Delete-User <username><br/>UCS Add-VLAN <Vlan Name>,<Vlan Number>")
 
    body_data = {"roomId": DEST_ROOM, "text": person_email + ":  you requested " + new_message}
    response_body = http_action('POST', API_URL + MESSAGES, POST_HEADERS, body_data)
    body_data = {"roomId": DEST_ROOM, "markdown": ucs_response}
    response_body = http_action('POST', API_URL + MESSAGES, POST_HEADERS, body_data)


def lambda_handler(event, context):
    '''
    Process the WebexTeams Message
    '''

    print("Received event: " + json.dumps(event, indent=2))
    if event['httpMethod'] == 'POST':
        if event['body']:
            payload = json.loads(event['body'])
            print("The Body: " + json.dumps(payload, indent=2))
            print("person Id")
            print(payload['data']['personId'])

            if payload['data']['personId'] != BOT_ID:
                return respond(None, process_msg(payload))
        else:
            return respond(None, 'No webhook body')
    else:
        return respond(ValueError('Unsupported method "{}"'.format(event['httpMethod'])))
