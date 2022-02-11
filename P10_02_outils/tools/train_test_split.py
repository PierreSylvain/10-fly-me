import argparse
import os
import json
import os.path
import math
import sys

# Intent labels
labels = ['dst_city','or_city','str_date','end_date','budget']

def get_entity_index(text, char):
    """
    Get position (start/end) of a substring

    Args:
        text (string): sentence
        char (string): substring to find position

    Returns:
        dic: start and end position
    """
    start = text.lower().index(char.lower())
    end = start + len(char)
    return {'start': start, 'end': end}

def get_entity(arg, text):
    """
    Get entity in a string

    Args:
        arg (array): definition of the entity
        text (string): sentence

    Returns:
        dic: Entity name and position in sentence
    """
    entity_label = {}

    # Only wanted entities
    try:
        if arg['val'] == "-1":
            return entity_label

        if arg['key'] in labels:
            char_index = get_entity_index(text, arg['val'])
            entity_label['startCharIndex'] = char_index['start']
            entity_label['endCharIndex'] = char_index['end']
            entity_label['entityName'] = arg['key']
    except KeyError:
        entity_label = {}


    return entity_label

def save_intents(outputfile, intents):
    """
    Save JSON LUIS intents into a file

    Args:
        outputfile (string): Destination filename
        intents (json): Data
    """
    with open(outputfile, 'w') as fp:
        json.dump(intents, fp)

def get_intents(turn, intent_text):
    """
    Get intents from json

    Args:
        turn (array): Json array
        intent_text (string): Intents to detects

    Returns:
        [type]: [description]
    """

    entity_labels = []
    intent_name = ""

    for act in turn['labels']['acts']:
        for arg in  act['args']:
            # Intent found
            if  arg['key'] == 'intent':
                intent_name = arg['val']
                continue

            # Get entities
            entity_label = get_entity(arg, intent_text)
            if entity_label:
                entity_labels.append(entity_label)

    if not intent_name:
        intent_name = "book"

    return intent_name, entity_labels

def convert_to_luis(filename, destination, train_size):
    """
    Convert JSON into LUIS Json

    Args:
        filename (string): JSON source filename
        destination (string): Folder destination for converted file
    """
    with open(filename) as json_file:
        data = json.load(json_file)

    intents_test = []
    intents_train = []

    stop_train = math.floor(len(data) * train_size)

    for conversation in data:
        # Get the first turn
        turn =  conversation['turns'][0]
        intent = {}
        intent['text'] = turn['text']
        intent['intentName'], entity_labels = get_intents(turn, intent['text'])
        intent['entityLabels'] = entity_labels

        if stop_train <= 0:
            intents_test.append(intent)
        else:
            intents_train.append(intent)
        stop_train -= 1

    # Save new JSON file
    outputfile = os.path.join(destination, 'frames_test.json')
    save_intents(outputfile, intents_test)
    print(f"New file generated {outputfile} with {len(intents_test)} records on {len(data)}")

    outputfile = os.path.join(destination, 'frames_train.json')
    save_intents(outputfile, intents_train)
    print(f"New file generated {outputfile} with {len(intents_train)} records on {len(data)}")

def get_train_test_size(train_size, test_size):
    """
    Get Test size from arguments or use default value

    Args:
        args (array): Command line args

    Raises:
        ValueError: Error in number

    Returns:
        list: train and test size
    """

    # Check if test size and train size are not set
    if test_size is None and train_size is None:
        test_size = 0.25
        train_size = 0.75

    # Set test size from train size
    if test_size is None and train_size >= 0.0:
        test_size = 1.0 - train_size

    # Set train size from test size
    if train_size is None and test_size >= 0.0:
        train_size = 1.0 - test_size

    # Check test size value
    if test_size > 1.0 or test_size < 0.0:
        raise ValueError("Wrong value for test size")

    # Check train size value
    if train_size > 1.0 or train_size < 0.0:
        raise ValueError("Wrong value for train size")

    # Check if sum if lower than 1
    if (train_size + test_size) > 1.0:
        raise ValueError("Sum of train size and test size is over 100%")

    return (train_size, test_size)

def parse_args(args):
    parser = argparse.ArgumentParser(description='Split json data into train/test data in LUIS format')

    help_in = """
    Filename of data in json format to extract.
    By default frames/frames.json
    """

    help_test_size = """
    Should be between 0.0 and 1.0 and represent the proportion of the dataset to include in the test split.
    If None, the value is set to the complement of the train size. If train_size is also None, it will be set to 0.25.
    Default: 0.25
    """

    help_train_size = """
    Should be between 0.0 and 1.0 and represent the proportion of the dataset to include in the train split.
    If None, the value is set to the complement of the test size. If test_size is also None, it will be set to 0.75.
    Default: 0.75
    """

    help_out = """
    Folder where to save in LUIS format the train set (frames_train.json) and test set (frames_test.json).
    Default: ./frames
    """

    parser.add_argument("--in", dest='input_file', type=str, default="./frames/frames.json", help=help_in)
    parser.add_argument("--test_size", dest='test_size', type=float, help=help_test_size)
    parser.add_argument("--train_size", type=float, help=help_train_size)
    parser.add_argument("--out", dest='folder', type=str, default="./frames",help=help_out)
    return parser.parse_args(args)


if __name__ == "__main__":


    args = parse_args(sys.argv[1:])

    # Check input file
    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} not found")
        exit();

    # Check destination folder
    try:
        os.makedirs(args.folder, exist_ok=True)
    except OSError as error:
        print("Unable to create Destination folder " + error)
        exit();

    # Check train/test split values
    try:
        train_size, test_size = get_train_test_size(args.train_size, args.test_size)
    except ValueError as error:
        print(error)
        exit();

    convert_to_luis(args.input_file, args.folder, train_size)
