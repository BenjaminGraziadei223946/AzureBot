import azure.functions as func
import logging
import requests
import json
from azure.communication.callingserver import (
    CallingServerClient,
    CallConnection,
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    CreateCallOptions,
    PhoneNumberIdentifier
)


app = func.FunctionApp()

def start_call(caller_id, target_id, client):
    call_options = CreateCallOptions(
        source=CommunicationUserIdentifier(caller_id),
        targets=[PhoneNumberIdentifier(target_id)],
        callback_uri="YOUR_CALLBACK_URI"  # Replace with your callback URI for call events
    )

    call_connection = client.create_call_connection(call_options)
    return call_connection.call_connection_id


def send_message_to_bot(message):
    # Generate a token using your Direct Line secret
    direct_line_secret = 'TB7IRiua2QM.yklPEm4vFZXpFN1MsIKOmrlwFgm3O3gsKe8Nyoult10'
    token_response = requests.post('https://directline.botframework.com/v3/directline/tokens/generate',
                                   headers={'Authorization': f'Bearer {direct_line_secret}'})
    token = token_response.json()['token']

    # Create a conversation
    conversation_response = requests.post('https://directline.botframework.com/v3/directline/conversations',
                                          headers={'Authorization': f'Bearer {token}'})
    conversation_id = conversation_response.json()['conversationId']

    requests.post(f'https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities',
                  headers={'Authorization': f'Bearer {token}'},
                  json=message)

@app.event_grid_trigger(arg_name="azeventgrid", auth_level=func.AuthLevel.ANONYMOUS)
def acceptCall(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event: %s', azeventgrid.event_type)

    # Define the webhook URL, which now points to the acsWebhook function within the same Function App
    webhook_url = 'https://eventcallback.azurewebsites.net/api/acswebhook'

    logging.info('Incoming call')
    response = requests.post(webhook_url, json=azeventgrid.get_json())

@app.route(route="acsWebhook", auth_level=func.AuthLevel.ANONYMOUS)
def acs_webhook(req: func.HttpRequest) -> func.HttpResponse:
    try:
        request_data = req.get_json()
        # Simulate a user message based on the event
        bot_message = {
            "type": "event",
            "name": "callEvent",  # This is the custom event name
            "value": {
                "eventType": request_data['eventType'],
                "callId": request_data.get('callId', 'Unknown')  # Include more details as needed
            }
        }
        send_message_to_bot(bot_message)
        # Forward this message to your Bot Framework Composer bot
        # [Insert logic to send this to your bot]
    except ValueError as e:
        logging.error('Failed to parse JSON: %s', e)
        return func.HttpResponse("Invalid JSON", status_code=400)
    
    return func.HttpResponse(f"Event processed, {bot_message}", status_code=200)

@app.route("/startcall", methods=["POST"])
def start_call_handler(req: func.HttpRequest) -> func.HttpResponse:
    connection_string = "endpoint=https://maxcomser.europe.communication.azure.com/;accesskey=sOLSdBBHU9tgsPa1QQ779r73xsz5S5U3T6+QSejGzItpTep2T1cz0cadvSJQNqz5lyWS2QicoGYXVnD5dhq91w=="  # Replace with your ACS connection string
    client = CallingServerClient.from_connection_string(connection_string)
    try:
        request_body = req.get_json()
        caller_id = request_body.get("caller_id")
        target_id = request_body.get("target_id")

        if not caller_id or not target_id:
            return func.HttpResponse(
                "Missing caller_id or target_id in the request body",
                status_code=400
            )

        call_connection_id = start_call(caller_id, target_id, client)
        return func.HttpResponse(
            f"Call started with connection ID: {call_connection_id}",
            status_code=200
        )

    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)
    except Exception as e:
        logging.error(f"Error starting call: {str(e)}")
        return func.HttpResponse("Error starting call", status_code=500)
