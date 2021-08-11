from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

import json, time, uuid

def load_json(file_name):

    with open(file_name, "r") as f:
        return json.load(f)

def get_grandchild_id(model, childName, grandChildName):

    theseChildren = next(filter((lambda child: child.name == childName), model.children))
    theseGrandchildren = next(filter((lambda child: child.name == grandChildName), theseChildren.children))

    grandChildId = theseGrandchildren.id

    return grandChildId

def quickstart():

    # Créez des variables pour stocker votre clé de création et les noms de vos ressources
    authoringKey = '6faee2d4ebfc40f7a51c549d67e0f60c'
    authoringEndpoint = 'https://westeurope.api.cognitive.microsoft.com/'
    predictionKey = '8cdd18ff30904d7eb39b2133a67034d5'
    predictionEndpoint = 'https://ocrp10name.cognitiveservices.azure.com/'

    # We use a UUID to avoid name collisions.
    # We use a UUID to avoid name collisions.
    appName = "Contoso Pizza Company " + str(uuid.uuid4())
    versionId = "0.1"
    intentNames = "OrderPizzaIntent"

    client = LUISAuthoringClient(authoringEndpoint, CognitiveServicesCredentials(authoringKey))
    # define app basics
    appDefinition = ApplicationCreateObject(name=appName, initial_version_id=versionId, culture='en-us')

    # create app
    app_id = client.apps.add(appDefinition)

    # get app id - necessary for all other changes
    print("Created LUIS app with ID {}".format(app_id))

    # Add intent
    client.model.add_intent(app_id, versionId, intentNames)

    # Create entities

    # Add Prebuilt entity


    client.model.add_prebuilt(app_id, versionId, prebuilt_extractor_names=["number"])

    # define machine-learned entity
    mlEntityDefinition = [
        {
            "name": "Pizza",
            "children": [
                {"name": "Quantity"},
                {"name": "Type"},
                {"name": "Size"}
            ]
        },
        {
            "name": "Toppings",
            "children": [
                {"name": "Type"},
                {"name": "Quantity"}
            ]
        }]

    # add entity to app
    modelId = client.model.add_entity(app_id, versionId, name="Pizza order", children=mlEntityDefinition)
    print("modelID",modelId)
    print("type modelID", type(modelId))
    # define phraselist - add phrases as significant vocabulary to app
    phraseList = {
        "enabledForAllModels": False,
        "isExchangeable": True,
        "name": "QuantityPhraselist",
        "phrases": "few,more,extra"
    }

    # add phrase list to app
    phraseListId = client.features.add_phrase_list(app_id, versionId, phraseList)

    # Get entity and subentities
    modelObject = client.model.get_entity(app_id, versionId, modelId)
    print("modelOBJECT",modelObject)
    print("type modelObject", type(modelObject))
    print("modelOBJECT.name", modelObject.name)
    toppingQuantityId = get_grandchild_id(modelObject, "Toppings", "Quantity")
    pizzaQuantityId = get_grandchild_id(modelObject, "Pizza", "Quantity")

    # add model as feature to subentity model
    prebuiltFeatureRequiredDefinition = {"model_name": "number", "is_required": True}
    client.features.add_entity_feature(app_id, versionId, pizzaQuantityId, prebuiltFeatureRequiredDefinition)

    # add model as feature to subentity model
    prebuiltFeatureNotRequiredDefinition = {"model_name": "number"}
    client.features.add_entity_feature(app_id, versionId, toppingQuantityId, prebuiltFeatureNotRequiredDefinition)

    # add phrase list as feature to subentity model
    phraseListFeatureDefinition = {"feature_name": "QuantityPhraselist", "model_name": None}
    client.features.add_entity_feature(app_id, versionId, toppingQuantityId, phraseListFeatureDefinition)




quickstart()