from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
import json
import time
import uuid
import argparse
import os

# Looking to go from San Francisco to MArseille with a budget of $2000
# 2022-01-01
# 2022-02_01

#I want to travel from  San francisco to Marseille on 2022-01-01 and return on 2022-05-01. with a budget of 2000.
#I want to travel from  San francisco to Marseille on next monday and return on 25 september with a budget of 2000.

def get_json(filename):
    """
    Load JSON file

    Args:
        filename (string): JSON filename

    Returns:
        list: JSON file content
    """
    with open(filename, "r") as jsonfile:
        content = json.load(jsonfile)
    return content


class CreateLUIS:
    VERSION = "0.1"
    INTENT_NAME = "FlyMeIntent"
    APP_NAME = "Fly Me " + str(uuid.uuid4())

    def __init__(self, trainset_file):
        """
        Init class

        Args:
            trainset_file (string): Filename for train set
        """
        self.train = trainset_file
        self.config = get_json("./config.json")
        self.create_application()
        self.create_intents()
        self.create_entities()
        self.add_utterance()
        self.train_version()
        self.publish()
        self.single_test()

    def create_application(self):
        """
        Create LUIS application
        """
        client = LUISAuthoringClient(
            self.config["authoringEndpoint"],
            CognitiveServicesCredentials(self.config["authoringKey"])
        )

        # define app basics
        app_definition = ApplicationCreateObject(
            name=self.APP_NAME, initial_version_id=self.VERSION, culture='en-us')

        # create app
        app_id = client.apps.add(app_definition)

        # get app id - necessary for all other changes
        print(f"Created LUIS app with ID {app_id}")
        self.client = client
        self.app_id = app_id
        print(f"Application ID: {app_id}")

    def create_intents(self):
        """
        Create intents
        """
        intents = ["book"]
        for intent in intents:
            self.client.model.add_intent(self.app_id, self.VERSION, intent)
            print(f"Created LUIS intent: {intent}")

    def add_entity(self, name, prebuilt_feature_not_nequired_definition):
        """
        Add entity to model

        Args:
            name (string): entity name
            prebuilt_feature_not_nequired_definition (feature_relation_create_object): A Feature relation information
        """
        entity = self.client.model.add_entity(
            self.app_id, self.VERSION, name=name)
        self.client.features.add_entity_feature(
            self.app_id, self.VERSION, entity, prebuilt_feature_not_nequired_definition)
        print(f"Entity: {name} added")

    def create_entities(self):
        """
        Create entities
        """
        # Prebuilt entities
        prebuilt_entities = ["datetimeV2", "money", "geographyV2"]
        self.client.model.add_prebuilt(
            self.app_id, self.VERSION, prebuilt_extractor_names=prebuilt_entities)
        print(f"Added prebuilt entities: {prebuilt_entities}")

        prebuilt_feature_not_required_definition_geography = {
            "model_name": "geographyV2", "is_required": False}
        prebuilt_feature_not_required_definition_datetime = {
            "model_name": "datetimeV2", "is_required": False}
        prebuilt_feature_not_required_definition_money = {
            "model_name": "money", "is_required": False}

        # App entities
        self.add_entity(
            "or_city", prebuilt_feature_not_required_definition_geography)
        self.add_entity(
            "dst_city", prebuilt_feature_not_required_definition_geography)
        self.add_entity(
            "str_date", prebuilt_feature_not_required_definition_datetime)
        self.add_entity(
            "end_date", prebuilt_feature_not_required_definition_datetime)
        self.add_entity(
            "budget", prebuilt_feature_not_required_definition_money)

    def add_utterance(self):
        """
        Read utterance from file and add them to model
        """
        utterances = get_json(self.train)

        for utterance in utterances:
            self.client.examples.add(self.app_id, self.VERSION, utterance, {
                                     "enableNestedChildren": True})
        print(f"{len(utterances)} utterances added")

    def train_version(self):
        """
        Train Model
        """
        self.client.train.train_version(self.app_id, self.VERSION)
        waiting = True
        while waiting:
            info = self.client.train.get_status(self.app_id, self.VERSION)

            # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
            waiting = any(map(
                lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
            if waiting:
                print("Waiting 10 seconds for training to complete...")
                time.sleep(10)
            else:
                print("Application trained")
                waiting = False

    def publish(self):
        """
        Publish model
        """
        try:
            self.client.apps.update_settings(self.app_id, is_public=True)
            self.client.apps.publish(
                self.app_id, self.VERSION, is_staging=False)
        except Exception as e:
            print("ERROR: " + e)

        print("Application published")

    def single_test(self):
        """
        Do a test and display result
        """
        if self.config["app_id"] is not None:
            self.app_id = self.config["app_id"]

        runtime_credentials = CognitiveServicesCredentials(
            self.config["predictionKey"])
        client_runtime = LUISRuntimeClient(
            endpoint=self.config["predictionEndpoint"], credentials=runtime_credentials)
        prediction_request = {
            "query": "Looking to go from San Francisco to MArseille. Book me for September 18 to 22. Let me know if its more than 2800 because thats all I can afford"}

        prediction_response = client_runtime.prediction.get_slot_prediction(
            self.app_id, "Production", prediction_request)
        print("Top intent: {}".format(prediction_response.prediction.top_intent))
        print("Sentiment: {}".format(prediction_response.prediction.sentiment))
        print("Intents: ")

        for intent in prediction_response.prediction.intents:
            print("\t{}".format(json.dumps(intent)))
        print("Entities: {}".format(prediction_response.prediction.entities))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create/train/publish/test LUID model')

    help_file = """
    Filename. File containing LUIS JSON file to train
    """

    parser.add_argument("--file", dest='input_file', type=str, help=help_file, required=True)
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} not found")
        exit();

    CreateLUIS(args.input_file)
