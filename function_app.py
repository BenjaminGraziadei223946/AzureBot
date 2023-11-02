import azure.functions as func
import logging
import requests

app = func.FunctionApp()

@app.event_grid_trigger(arg_name="azeventgrid")
def acceptCall(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event: %s', azeventgrid.event_type)

    # Define the webhook URL, which now points to the acsWebhook function within the same Function App
    webhook_url = 'https://EventCallback.azurewebsites.net/api/acsWebhook'

    if azeventgrid.event_type == 'Microsoft.Communication.IncomingCall':
        logging.info('Incoming call')
        bot_data = {
            'type': 'incomingCall',
            'data': azeventgrid.data
        }
        # Send data to Microsoft Teams bot via a webhook
        response = requests.post(webhook_url, json=bot_data)

        logging.info('Sent event data to webhook: %s', response.status_code)

    # ... (handle other event types as needed)

@app.route(route="acsWebhook", auth_level=function.AuthLevel.ANONYMOUS)
def acs_webhook(req: func.HttpRequest) -> func.HttpResponse:
    # Extract information from the Event Grid event
    event_data = req.get_json()  # Assume the request body contains the event data in JSON format

    # Check if the event is an incoming call
    logging.info('Incoming call')
    

    return func.HttpResponse("Data forwarded to Microsoft Teams bot", status_code=200)
