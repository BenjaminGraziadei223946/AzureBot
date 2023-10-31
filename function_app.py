import logging
import azure.functions as func
import azure.cognitiveservices.speech as speechsdk
import openai
import os

openai.api_key = os.environ.get('api_key')
openai.api_base = os.environ.get('api_base')
openai.api_type = os.environ.get('api_type')
openai.api_version = os.environ.get('api_version')
speech_key = os.environ.get('speech_key')
service_region = os.environ.get('service_region')
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"

# Creates a speech synthesizer using the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

conversation = [{"role": "system", "content": ""}]
init_prompt = f"Greet the customer and ask how you can help them."

def reset():
    speech_synthesizer.stop_speaking_async()
    

def generate_response(prompt):
    conversation.append({"role": "user", "content":prompt})
    completion=openai.ChatCompletion.create(
        engine = "PvA",
        model="gpt-3.5-turbo",
        messages = conversation
    )
    
    message=completion.choices[0].message.content
    return message

def onStart():
    init_response = generate_response(init_prompt)
    speech_synthesizer.speak_text_async(init_response).get()
    conversation.append({"role": "user", "content":init_prompt})
    conversation.append({"role": "assistant", "content":init_response})

def recognition():
    while True:
        result = ""
        text = ""
        text = speech_recognizer.recognize_once().text

        if text:
            if text == "exit." or text == "Exit.":
                break
            result = generate_response(text)
            conversation.append({"role": "assistant", "content":result})

        if result:
            #output.write(result)        # result
            speech_synthesizer.speak_text_async(result).get()


app = func.FunctionApp()

@app.event_grid_trigger(arg_name="azeventgrid")
def acceptCall(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event: %s', azeventgrid.event_type)

    if azeventgrid.event_type == 'Microsoft.Communication.IncomingCall':
        #onStart()
        logging.info('Incoming call')
    elif azeventgrid.event_type == 'Microsoft.Communication.CallStarted':
        #recognition()
        logging.info('Call started')
    elif azeventgrid.event_type == 'Microsoft.Communication.CallEnded':
        #reset()
        logging.info('Call ended')
