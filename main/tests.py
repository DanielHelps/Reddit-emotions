# Create your tests here.
from xmlrpc import client
from django.test import TestCase
from .classifier_functions import find_expressions
from django.test.utils import setup_test_environment
from django.test import Client
from django.urls import reverse

class TestViews(TestCase):
    def setUp(self):
        setup_test_environment()
        
        
    def test_home_view(self):
        client = Client()
        response = client.get(reverse('home'))

class ExpressionsTestCase(TestCase):

    def test_expressions_func(self):
        # result = 10+1
        # self.assertEqual(result, 1)
        sentence = "WOW i am so happy :)"
        sad_expressions = [":(", ":'(", ":-(", ":'-(", "=("]
        happy_expressions = [":)", ":-)", ":D", "=)", ":]", ":>", ":^)"]
        """Check edge cases of sentences"""
        self.assertEqual(find_expressions(sentence, sad_expressions, happy_expressions), 1)


