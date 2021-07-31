# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    CANCEL = "Cancel"
    GET_WEATHER = "GetWeather"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "To", []
                )
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.destination = to_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            to_entities[0]["text"].capitalize()
                        )

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "From", []
                )
                if len(from_entities) > 0:
                    if recognizer_result.entities.get("From", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.origin = from_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            from_entities[0]["text"].capitalize()
                        )
                #https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-reference-prebuilt-currency?tabs=V3
                budget_entities = recognizer_result.entities.get("money", [])
                #print("luis_helper - 85")
                #print(budget_entities)
                if budget_entities:
                    #print(result.budget)
                    result.budget = str(budget_entities[0]["number"]) + " " + budget_entities[0]["units"]
                    print(result.budget)
                else:
                    result.budget = None

                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                departure_date_entities = recognizer_result.entities.get("datetime", [])
                #print("luis_helper")
                #print(departure_date_entities)
                #print(len(departure_date_entities))
                #print(departure_date_entities[0]["type"])

                if departure_date_entities and len(departure_date_entities) == 1 and departure_date_entities[0]["type"] == 'date':
                    #print("A")
                    timex = departure_date_entities[0]["timex"]

                    if timex:
                        datetime = timex[0].split("T")[0]

                        result.departure_date = datetime
                        print(result.departure_date)
                else:
                    if departure_date_entities and len(departure_date_entities) == 1 and departure_date_entities[0][
                        "type"] == 'daterange':
                        #print("B")
                        timex = departure_date_entities[0]["timex"]

                        if timex:
                            datetime = timex[0].split("T")[0][1:11]

                            result.departure_date = datetime
                            print(datetime)
                    else:
                        if departure_date_entities and len(departure_date_entities) == 2:
                            #print("C")
                            timex = departure_date_entities[0]["timex"]

                            if timex:
                                datetime = timex[0].split("T")[0]

                                result.departure_date = datetime

                            else:
                                #print("D")
                                result.departure_date = None

                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                return_date_entities = recognizer_result.entities.get("datetime", [])
                #print("luis_helper")
                #print(return_date_entities)

                if return_date_entities and len(return_date_entities) == 1 and return_date_entities[0]["type"] == 'date':
                    #print("E")
                    result.return_date = None

                else:
                    if return_date_entities and len(return_date_entities) == 1 and return_date_entities[0][
                        "type"] == 'daterange':
                        #print("F")
                        timex = return_date_entities[0]["timex"]
                        #print(timex)
                        if timex:
                            datetime = timex[0].split("T")[0][12:22]

                            result.return_date = datetime
                            #print(datetime)
                    else:
                        if return_date_entities and len(return_date_entities) == 2:
                            #print("G")
                            timex = return_date_entities[1]["timex"]

                            if timex:
                                datetime = timex[0].split("T")[0]

                                result.return_date = datetime

                            else:
                                #print("H")
                                result.return_date = None

        except Exception as exception:
            print(exception)

        return intent, result
