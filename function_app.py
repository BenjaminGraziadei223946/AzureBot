import azure.functions as func
import logging
import requests
from azure.communication.callautomation import CallAutomationClient, IncomingCallContext
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

def accept_incoming_call(call_id):
    # Initialize the CallAutomationClient
    call_client = CallAutomationClient("endpoint=https://maxcomser.europe.communication.azure.com/;accesskey=sOLSdBBHU9tgsPa1QQ779r73xsz5S5U3T6+QSejGzItpTep2T1cz0cadvSJQNqz5lyWS2QicoGYXVnD5dhq91w==", DefaultAzureCredential())

    # Get the context for the incoming call
    incoming_call_context = IncomingCallContext(call_id)

    # Answer the call
    call_connection = call_client.answer_call(incoming_call_context)
    # Additional logic for call handling can be added here


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

@app.route(route="acceptCall", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def handle_incoming_call(req: func.HttpRequest) -> func.HttpResponse:
    try:
        request_data = req.get_json()
        call_id = request_data['data']['callId']
        accept_incoming_call(call_id)
        return func.HttpResponse("Call accepted", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)