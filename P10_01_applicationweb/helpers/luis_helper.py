# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "book"
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
        """Returns an object with preformatted LUIS results for the bot's dialogs to consume."""
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

                # Destination -------------------------------
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "dst_city", []
                )
                if len(to_entities) > 0:
                    # Just guess that there is an airport here
                    result.destination = to_entities[0]["text"].capitalize()

                # From --------------------------------------
                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "or_city", []
                )
                if len(from_entities) > 0:
                    # Just guess that there is an airport here
                    result.origin = from_entities[0]["text"].capitalize()

                # Departure ---------------------------------
                departure_date_entities = recognizer_result.entities.get("str_date", [])
                result.departure_date = None
                if departure_date_entities:
                    datetime_entities = recognizer_result.entities.get("datetime", [])
                    if datetime_entities[0]['type'] == "date":
                        result.departure_date = datetime_entities[0]['timex'][0]

                # Return -------------------------------------
                return_date_entities = recognizer_result.entities.get("end_date", [])
                result.return_date = None
                if return_date_entities:
                    # Sometimes it's a list
                    if isinstance(return_date_entities, list):
                        result.return_date = ' '.join(return_date_entities)
                    else:
                        result.return_date = return_date_entities[0]["str_date"]

                # Datetime --------------
                datetime_entities = recognizer_result.entities.get("datetime", [])
                if datetime_entities[0]['type'] == "daterange":
                    result.departure_date = datetime_entities[0]['timex'][0].split(',')[0].strip('(')
                    result.return_date = datetime_entities[0]['timex'][0].split(',')[1].strip(')')

                # Budget --------------------------------------
                budget_entities = recognizer_result.entities.get("$instance", {}).get(
                    "budget", []
                )
                result.budget = None
                if len(budget_entities) > 0:
                    result.budget = "$" + budget_entities[0]["text"].capitalize()

        except Exception as exception:
            print(exception)

        return intent, result
