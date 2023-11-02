import azure.functions as func
import logging
import requests

app = func.FunctionApp()

@app.event_grid_trigger(arg_name="azeventgrid")
def acceptCall(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event: %s', azeventgrid.event_type)

    # Define the webhook URL, which now points to the acsWebhook function within the same Function App
    webhook_url = 'https://eventcallback.azurewebsites.net/api/acswebhook'

    logging.info('Incoming call')
    response = requests.post(webhook_url, json=azeventgrid.get_json())
    return func.HttpResponse("Data forwarded to Microsoft Teams bot", status_code=200)

@app.route(route="acsWebhook", auth_level=func.AuthLevel.ANONYMOUS)
def acs_webhook(req: func.HttpRequest) -> func.HttpResponse:
    # Extract information from the Event Grid event
    try:
        request_data = req.get_json()
    except ValueError as e:
        logging.error('Failed to parse JSON: %s', e)
        return func.HttpResponse("Invalid JSON", status_code=400)
    
    request_data = req.get_json()
    # ...
    return func.HttpResponse(body=request_data, status_code=200, mimetype="application/json")
