""" Lambda function to copy message to a destination room and notify sender """

import json
import os
import requests
import ucsm_operations

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_ID = os.environ['BOT_ID']
DEST_ROOM = os.environ['DEST_ROOM']

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
    """ Return request status """
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def http_action(http_method, api_url, http_headers, body_data=None):
    """ Run specified HTTP Method with Supplied parameters """

    if http_method == 'GET':
        response = requests.get(api_url, headers=http_headers, verify=True)
    elif http_method == 'POST':
        response = requests.post(
            api_url, headers=http_headers, data=json.dumps(body_data), verify=True)

    print(response)

    return response.json()


def process_msg(payload):
    """
    Get the message
      - Send to Destination Team roomId
      - Send confirmation to sender
    """

    #person_id = payload['data']['personId']
    person_email = payload['data']['personEmail']
    message_id = payload['data']['id']

    print("Message Id")
    print(payload['data']['id'])

    response_body = http_action('GET', API_URL + MESSAGES + "/" + message_id, GET_HEADERS)
    print('Message Get Response')
    print(response_body)

    orig_message = response_body['text']
    new_message = orig_message.lower()
    print(new_message)

    ucs_response = "no operation requested or understood"
    if "ucs get-inventory" in new_message:
        ucs_response = ucsm_operations.get_ucs_inventory()

    if "ucs get-faults" in new_message:
        ucs_response = ucsm_operations.get_ucs_faults()

    command = "ucs org"
    if command in new_message:
        inputs = [x.strip(' \t\n\r') for x in orig_message[orig_message.index(command)+len(command):].split(',')]
        print(inputs)
        ucs_response = ucsm_operations.manage_org(inputs)

    command = "ucs vmedia"
    if command in new_message:
        inputs = [x.strip(' \t\n\r') for x in orig_message[orig_message.index(command)+len(command):].split(',')]
        print(inputs)
        ucs_response = ucsm_operations.manage_vmedia(inputs)

    if "help" in new_message:
        ucs_response = (
            "Possible Operations:<br/>" +
            "UCS Get-Inventory<br/>" +
            "UCS Get-Faults<br/>" +
            "UCS Org `<add|update|remove>, <parent_org>, <name>, [<descr>]`</br>" +
            "UCS Vmedia-Policy `<add|update>, <org>, <policy_name>,`</br>" +
            "                  `[<mount_name>], [<image_path], [image_image>]`</br>" +
            "UCS Vmedia-Policy `<remove>, <org>, <policy_name>, [<mount_name>]`</br>"
            )

    body_data = {"roomId": DEST_ROOM, "text": person_email + ":  you requested " + orig_message}
    response_body = http_action('POST', API_URL + MESSAGES, POST_HEADERS, body_data)
    body_data = {"roomId": DEST_ROOM, "markdown": ucs_response}
    response_body = http_action('POST', API_URL + MESSAGES, POST_HEADERS, body_data)


def lambda_handler(event, context):
    """ Process the Webex Teams Message """

    print("Received event: " + json.dumps(event, indent=2))
    print("Received context:")
    print(context)

    if event['httpMethod'] == 'POST':
        if event['body']:
            payload = json.loads(event['body'])
            print("The Body: " + json.dumps(payload, indent=2))

            if payload['data']['personId'] != BOT_ID:
                return respond(None, process_msg(payload))
        else:
            return respond(None, 'No webhook body')
    else:
        return respond(ValueError('Unsupported method "{}"'.format(event['httpMethod'])))
