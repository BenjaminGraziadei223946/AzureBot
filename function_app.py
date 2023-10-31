import logging
import azure.functions as func


app = func.FunctionApp()

@app.event_grid_trigger(arg_name="azeventgrid")
def acceptCall(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event: %s', azeventgrid.event_type)

    if azeventgrid.event_type == 'Microsoft.Communication.IncomingCall':
        logging.info('Incoming call')
    elif azeventgrid.event_type == 'Microsoft.Communication.CallStarted':
        logging.info('Call started')
    elif azeventgrid.event_type == 'Microsoft.Communication.CallEnded':
        logging.info('Call ended')
