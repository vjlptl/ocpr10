from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

import json, time, uuid

def get_child_id(model, childName):

    theseChildren = next(filter((lambda child: child.name == childName), model.children))
    ChildId = theseChildren.id

    return ChildId

def load_json(file_name):

    with open(file_name, "r") as f:
        return json.load(f)

def quickstart():

    # Créez des variables pour stocker votre clé de création et les noms de vos ressources
    authoringKey = '6faee2d4ebfc40f7a51c549d67e0f60c'
    authoringEndpoint = 'https://westeurope.api.cognitive.microsoft.com/'
    predictionKey = '8cdd18ff30904d7eb39b2133a67034d5'
    predictionEndpoint = 'https://ocrp10name.cognitiveservices.azure.com/'

    # We use a UUID to avoid name collisions.
    appName = "Book a flight " + str(uuid.uuid4())
    versionId = "0.1"
    intentNames = ["BookFlight", "Confirm", "Greetings"]

    client = LUISAuthoringClient(authoringEndpoint, CognitiveServicesCredentials(authoringKey))
    #print(client)

    # define app basics
    #appDefinition = ApplicationCreateObject(name=appName, initial_version_id=versionId, culture='en-us')
    appDefinition = {
        "name": appName,
        "initial_version_id": versionId,
        "culture": "en-us"
    }

    # create app
    app_id = client.apps.add(appDefinition)

    # get app id - necessary for all other changes
    print("Created LUIS app with ID {}".format(app_id))

    # Add intent
    for intent in intentNames:
        client.model.add_intent(app_id, versionId, intent)

    # Create entities

    # Add pre_built entity :
    client.model.add_prebuilt(app_id, versionId, prebuilt_extractor_names=["money", "geographyV2", "datetimeV2"])

    # Create Airport entity :
    airport_entity = {"name": "Airport"}

    # Add ML entity to app
    from_entity = client.model.add_entity(app_id, versionId, name="From", children=[airport_entity])
    to_entity = client.model.add_entity(app_id, versionId, name="To", children=[airport_entity])

    departure_date_id = client.model.add_entity(app_id, versionId, name="Departure_date")
    return_date_id = client.model.add_entity(app_id, versionId, name="Return_date")
    budget_id = client.model.add_entity(app_id, versionId, name="budget")

    # Get entity and sub-entities for nested entities:
    from_object = client.model.get_entity(app_id, versionId, from_entity)
    to_object = client.model.get_entity(app_id, versionId, to_entity)

    #print("Current test value ----- ", from_object)
    #print("Type ------------------- ", type(from_object))

    from_airport_id = get_child_id(from_object, "Airport")
    to_airport_id = get_child_id(to_object, "Airport")

    # Add model as feature to subentity model
    prebuiltFeaturedDefinition = {"model_name": "geographyV2", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, from_airport_id, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, to_airport_id, prebuiltFeaturedDefinition)
    prebuiltFeaturedDefinition = {"model_name": "datetimeV2", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, departure_date_id, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, return_date_id, prebuiltFeaturedDefinition)
    prebuiltFeaturedDefinition = {"model_name": "money", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, budget_id, prebuiltFeaturedDefinition)

    # Add utterances examples to intents

    # Define labeled examples :
    BookFlight_json_file = "./data/training_data_50_ex.json"
    BookFlight_utterance = load_json(BookFlight_json_file)
    #print("\nBookFlight_utterance : ", BookFlight_utterance)
    print("\n Number of BookFlight_utterances : ", len(BookFlight_utterance))

    other_utterances = [
        {
            "text": "right",
            "intentName": intentNames[1]
        },
        {
            "text": "yes",
            "intentName": intentNames[1]
        },
        {
            "text": "OK",
            "intentName": intentNames[1]
        }, {
            "text": "good",
            "intentName": intentNames[1]
        },
        {
            "text": "Hello",
            "intentName": intentNames[2]
        },
        {
            "text": "Hi",
            "intentName": intentNames[2]
        },
        {
            "text": "Hey",
            "intentName": intentNames[2]
        },
        {
            "text": "Good morning",
            "intentName": intentNames[2]
        }
    ]

    # Add an example for the entity
    # Enable nested children to allow using multiple models with the same name
    # The "quantity" subentity and the phraselise could have the same exact name if this is set to True

    for utterance in BookFlight_utterance:
        #print("\nutterance : ", utterance)
        client.examples.add(app_id, versionId, utterance, {"enableNestedChildren": True})
    for utterance in other_utterances:
        client.examples.add(app_id, versionId, utterance, {"enableNestedChildren": False})

    # Train the model ---------------------------------------------------------

    client.train.train_version(app_id, versionId)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id, versionId)

        # get_status returns a list of training statuses , one for each model. Loop through them and make sure all are done.
        waiting = any(map(lambda x: "Queued" == x.details.status or "InProgess" == x.details.status, info))
        if waiting:
            print("Waiting 10 seconds for training to complete")
            time.sleep(10)
        else:
            print("Trained")
            waiting = False


    # Mark the app as public so we can query it using any prediction endpoint.
    # Note: For production scenarios, you should instead assign the app to your own LUIS prediction endpoint. See:
    # https://docs.microsoft.com/en-gb/azure/cognitive-services/luis/luis-how-to-azure-subscription#assign-a-resource-to-an-app
    client.apps.update_settings(app_id, is_public=True)
    print(app_id)
    print(versionId)
    responseEndpointInfo = client.apps.publish(app_id, versionId, is_staging=False)
    print("Model published to Production slot")

    runtimeCredentials = CognitiveServicesCredentials(predictionKey)
    clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, credentials=runtimeCredentials)

    # Production == slot name
    predictionRequest = {"query": "Hi. i'd like to fly from New-York to Las-Vegas on August 10, 2021"}

    predictionResponse = clientRuntime.prediction.get_slot_prediction(app_id, "Production", predictionRequest)
    print("Top intent: {}".format(predictionResponse.prediction.top_intent))
    print("Sentiment: {}".format(predictionResponse.prediction.sentiment))
    print("Intents: ")

    for intent in predictionResponse.prediction.intents:
        print("\t{}".format(json.dumps(intent)))
    print("Entities: {}".format(predictionResponse.prediction.entities))

quickstart()