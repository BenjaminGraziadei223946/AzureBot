import azure.functions as func
import logging
import requests
import json


app = func.FunctionApp()

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
