

import uuid
import os.path
import json
import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir) + '/tools'
sys.path.insert(0, parentdir)
import train_test_split


class test_train_test_split(unittest.TestCase):

    """Test train/test split"""

    def test_get_entity_index(self):
        """Test if found entity index is the right one"""
        text =  'My name is Roberto'
        char = 'name'
        expected =  {'start': 3, 'end': 7}
        self.assertEqual(train_test_split.get_entity_index(text, char), expected)

    def test_get_entity(self):
        """Test if found entity is the right one"""
        arg = {'val': 'Atlantis', 'key': 'dst_city'}
        text = "I'd like to book a trip to Atlantis from Caprica on Saturday"
        expected = {'startCharIndex': 27, 'endCharIndex': 35, 'entityName': 'dst_city'}
        self.assertEqual(train_test_split.get_entity(arg, text), expected)

    def test_save_intents(self):
        """Test if to save intents to a file"""
        outputfile = str(uuid.uuid4()) + ".tmp"
        intents = {'filename': outputfile}
        train_test_split.save_intents(outputfile, intents)
        self.assertTrue(os.path.isfile(outputfile))

        with open(outputfile) as json_file:
            data = json.load(json_file)
        self.assertEqual(intents, data)
        os.remove(outputfile)

    def test_get_train_test_size(self):
        """Test all possible parameters for the size of test and train set"""
        self.assertEqual(train_test_split.get_train_test_size(0.20, 0.80), (0.20, 0.80))
        self.assertEqual(train_test_split.get_train_test_size(0.20, None), (0.20, 0.80))
        self.assertEqual(train_test_split.get_train_test_size(None, None), (0.75, 0.25))
        with self.assertRaises(ValueError):
            train_test_split.get_train_test_size(100, 10)
            train_test_split.get_train_test_size(-100, 10)
            train_test_split.get_train_test_size(100, 100)
            train_test_split.get_train_test_size(0.90, 0.20)

    def test_parser(self):
        """Test command line parameters"""
        parser = train_test_split.parse_args(['--in', 'filename'])
        self.assertEqual(parser.input_file, 'filename')

        parser = train_test_split.parse_args(['--test_size', '0.20'])
        self.assertEqual(parser.test_size, 0.20)

        parser = train_test_split.parse_args(['--train_size', '0.40'])
        self.assertEqual(parser.train_size, 0.40)

        parser = train_test_split.parse_args(['--out', 'folder'])
        self.assertEqual(parser.folder, 'folder')

if __name__ == '__main__':
    unittest.main()
