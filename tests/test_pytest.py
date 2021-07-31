import requests
import json

examples = {'BookFlight' : "Book a flight for paris",
            'GetWeather' : "What's the weather like?",
            'Cancel' : "Cancel the request please"}

def return_intent(query_):

    query_up = 'https://ocrp10name.cognitiveservices.azure.com/luis/prediction/v3.0/apps/fa4cfa08-373d-4c8d-84fd-3423d3e8814c/slots/production/predict?subscription-key=6faee2d4ebfc40f7a51c549d67e0f60c&verbose=true&show-all-intents=true&log=true&query='+query_
    r = requests.get(query_up)
    return json.loads(r.text)['prediction']['topIntent']



def test_booking():
    assert return_intent(examples['BookFlight']) == 'BookFlight'
def test_cancelling():
    assert return_intent(examples['Cancel']) == 'Cancel'
def test_weather():
    assert return_intent(examples['GetWeather']) == 'GetWeather'


