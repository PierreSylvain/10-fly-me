import json
import requests
import time
import argparse
import os

# Labels
labels = ['dst_city','or_city','str_date','end_date','budget']

def get_json(filename):
    """Load JSON file
    Args:
        filename (string): JSON filename

    Returns:
        list: JSON file content
    """
    with open(filename, "r") as jsonfile:
        content = json.load(jsonfile)
    return content

class Predict:
    def __init__(self):
        """
        Init Prdict class
        """
        self.config = get_json("./config.json")
        self.accuracy = {
            "intent": 0,
            "dst_city": 0,
            "or_city": 0,
            "str_date": 0,
            "end_date": 0,
            "budget": 0,
            "accuracy": 0
        }

    def luis_predict(self, query):
        """
        Call LUIS Predict and return detailed prediction

        Args:
            query (string): Sentence

        Returns:
            dict: detailed prediction
        """
        params ={
            'query': query,
            'timezoneOffset': '0',
            'verbose': 'true',
            'show-all-intents': 'true',
            'spellCheck': 'false',
            'staging': 'false',
            'subscription-key': self.config["predictionKey"]
        }

        headers = {
        }

        prediction_endpoint = self.config["predictionEndpoint"]
        app_id = self.config["app_id"]

        response = requests.get(f'{prediction_endpoint}luis/prediction/v3.0/apps/{app_id}/slots/production/predict', headers=headers, params=params)
        return response.json()

    def check_intent(self, utterance_intent, intent):
        """
        Check if predicted intent is the same as in the test intent

        Args:
            utterance_intent (string): test utterance
            intent (string): inetnet name
        """
        if(utterance_intent == intent):
            self.update_accuracy("intent",1)

    def update_accuracy(self, key, value, action=None):
        """
        Update accurante dictonnary

        Args:
            key (string): key name
            value (float): value
            action (string, optional): if "mean": calculate mean, by befaults it's sum
        """
        value = value + self.accuracy[key]

        if action == 'mean':
            value = value / 2.0

        self.accuracy.update({key: value})

    def check_entities(self, utterance, prediction):
        """
        Check predicted entities

        Args:
            utterance (dict): ground truth
            prediction (dict): predicted entities
        """
        entity_count = len(utterance)
        acuracy_count = 0
        for entity_label in utterance:
            entity_name = entity_label['entityName']

            try:
                prediction_instance = prediction["$instance"]
                if entity_name == prediction_instance[entity_name][0]["type"]:
                    self.update_accuracy(entity_name, 1, "mean")
                    acuracy_count += 1

            except KeyError:
                pass
        if entity_count == 0:
            entity_count = 1
        self.update_accuracy("accuracy", acuracy_count / entity_count, "mean")

    def predict(self, filename, count=4):
        """
        Do preidctions

        Args:
            filename (string): LUIS JSON file
            count (int, optional): Number of sentence to analyse. Defaults to 4. Can be "all"

        Returns:
            [type]: [description]
        """
        utterances = get_json(filename)

        # All utterances
        if count == "all":
            count = len(utterances)

        for utterance in utterances:
            response = self.luis_predict(utterance['text'])
            self.check_intent(utterance["intentName"], response["prediction"]["topIntent"])
            self.check_entities(utterance["entityLabels"],response["prediction"]["entities"])

            # Stop when all required utterances have been predicted
            count -= 1
            if count <= 0:
                break

            # Take a break to stay in Free slot
            time.sleep(1)

        return self.accuracy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test predictions from LUIS JSON file and return detailed accuracy')

    help_file = """
    Filename. This file containts LUIS intents to be tested.
    """

    help_count = """
    Number of intents to process. 'All' with process all records. Default 4
    """
    parser.add_argument("--file", dest='input_file', type=str, help=help_file, default=4, required=True)
    parser.add_argument("--count", dest='count', type=int, default=4, help=help_count)
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} not found")
        exit();

    predict = Predict()
    predictions = predict.predict(args.input_file, args.count)
    print(predictions)
