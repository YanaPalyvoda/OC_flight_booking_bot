# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from datatypes_date_time.timex import Timex

from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    CANCEL = "Cancel"
    #GET_WEATHER = "GetWeather"
    NONE_INTENT = "None"


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
        Returns an object with pre-formatted LUIS results for the bot's dialogs to consume.
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

                # We need to get the result from the LUIS JSON which at every level
                # returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "To", []
                )
                if len(to_entities) > 0:
                    result.destination = to_entities[0]["text"].capitalize()
                else:
                    result.destination =None
                    

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "From", []
                )
                if len(from_entities) > 0:
                    result.origin = from_entities[0]["text"].capitalize()
                else:
                    result.origin = None    

                # This value will be a TIMEX. And we are only interested in a Date so
                # grab the first result and drop the Time part.
                # TIMEX is a format that represents DateTime expressions that include
                # some ambiguity. e.g. missing a Year.
                datetimeOn = None
                datetimeEnd = None
                date_entities = recognizer_result.entities.get("datetime", [])
                if date_entities:
                    if len(date_entities)== 1:
                        timex = date_entities[0]["timex"] 
                        if date_entities[0]["type"]=="daterange":                       
                            dates = timex[0].replace('(', '').replace(')','').split(",")
                            datetimeOn = dates[0]                                                  
                            datetimeEnd = dates[1] 
                        elif date_entities[0]["type"]=="date":
                             datetimeOn = timex
                    else:
                        for dt in date_entities:
                            if dt["type"]=="date":
                                datetimeOn = dt["timex"][0]
                            if dt["type"]=="duration":
                                duration = dt["timex"][0]                

                                          
                result.on_date = datetimeOn
                result.end_date = datetimeEnd        

                budget_entities = recognizer_result.entities.get("$instance", {}).get(
                    "money", []
                )
                if len(budget_entities) > 0:
                    result.budget = budget_entities[0]["text"]
                else:
                    result.budget = None    

        except Exception as err:
            print(err)

        return intent, result
