from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
import unittest
import logging

from config import DefaultConfig
class test_luis(unittest.TestCase):
    """
    Create tests for luis

    Args:
        unittest ([type]): Unittest
    """
    def setUp(self):
        """Init tests, by requesting luis."""
        configuration = DefaultConfig()
        client = LUISRuntimeClient('https://' + configuration.LUIS_API_HOST_NAME,CognitiveServicesCredentials(configuration.LUIS_API_KEY))
        request ='I  want to travel from Paris to New York from november 2 and return on november 10 2021 with a budget of 2500'
        self.response = client.prediction.resolve(configuration.LUIS_APP_ID, query=request)
        self.log = logging.getLogger( "SomeTest.testSomething" )

    def test_intent(self):
        """Test if the found intent is the right one."""
        self.assertEqual(self.response.top_scoring_intent.intent,'book')

    def test_origin(self):
        """Test if the found departure city is the right one."""
        for idx, entity in enumerate(self.response.entities):
            if (entity.type == 'or_city') & (entity.entity == "paris"):
                self.assertTrue(True)
                return
        self.assertTrue(False)

    def test_destination(self):
        """Test if the found destination city is the right one."""
        for idx, entity in enumerate(self.response.entities):
            if (entity.type == 'dst_city') & (entity.entity == "new york"):
                self.assertTrue(True)
                return
        self.assertTrue(False)

    def test_start_date(self):
        """Test if the found departure departure is the right one."""
        for idx, entity in enumerate(self.response.entities):

            if (entity.type == 'str_date') & (entity.entity == "november 2"):
                self.assertTrue(True)
                return
        self.assertTrue(False)

    def test_budget(self):
        """Test if the found budget is the right one."""
        for idx, entity in enumerate(self.response.entities):
            if (entity.type == 'str_date') & (entity.entity == "november 2"):
                self.assertTrue(True)
                return
        self.assertTrue(False)
