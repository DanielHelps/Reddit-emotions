# Create your tests here.
from urllib import response
from django.test import TestCase, Client
from .classifier_functions import find_expressions
from django.urls import reverse
from .forms import Emotion_Search
from .models import SearchQ, Sentence
from .views import get_pos_neg_sens
from . import emotion_check

class ViewsTestCase(TestCase):
    def setUp(self) -> None:
        query = 'test'
        self.client = Client()
        self.home_url = reverse('home')
        self.emote_search = Emotion_Search()
        positive_1 = Sentence.objects.create(sentence="pos1", sentence_score=0.8)
        positive_2 = Sentence.objects.create(sentence="pos2", sentence_score=0.7)
        positive_3 = Sentence.objects.create(sentence="pos3", sentence_score=0.6)
        negative_1 = Sentence.objects.create(sentence="neg1", sentence_score=-0.8)
        negative_2 = Sentence.objects.create(sentence="neg2", sentence_score=-0.7)
        negative_3 = Sentence.objects.create(sentence="neg3", sentence_score=-0.6)
        self.search_obj = SearchQ.objects.create(query=query, score=85.0)
        self.search_obj.most_positive.set([positive_1, positive_2, positive_3])
        self.search_obj.most_negative.set([negative_1, negative_2, negative_3])
        self.search_obj.save()
        
    def test_home_view_regular_GET(self):
        response = self.client.get(self.home_url)
        self.assertEquals(response.status_code, 200)
        
    def test_home_value_invalid(self):
        # If search value is not valid
        response = self.client.get(self.home_url, {
            'search_but':'clicked'
        })
        self.assertEqual(str(response.content), "b'Problem, go back!'")
        
    def test_home_value_valid_db_nonexist(self):
        # When value is valid but query doesn't exists in database
        query = 'another_test'
        response = self.client.get(self.home_url, {
            'search_but':'clicked',
            'search_query': query,
            })
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, expected_url=f"/search={query}/1")
        
        
    def test_home_value_valid_db_exists(self):
        # When value is valid and query exists in database
        query = 'test'
        response = self.client.get(self.home_url, {
            'search_but':'clicked',
            'search_query': query
            })
        # checks that get_pos_neg_sens works properly
        sorted_sentences = get_pos_neg_sens(self.search_obj)
        
        
        self.assertEqual(len(get_pos_neg_sens(self.search_obj)),6)
            
        for i, sentence in enumerate(sorted_sentences[1:3]):
            # print(i)
            # print(sentence.sentence_score)
            # print(sorted_sentences[i].sentence_score)
            self.assertLessEqual(sentence.sentence_score,sorted_sentences[i].sentence_score)    
        
        for i, sentence in enumerate(sorted_sentences[4:6]):
            # print(i)
            # print(sentence.sentence_score)
            # print(sorted_sentences[i+3].sentence_score)
            self.assertGreaterEqual(sentence.sentence_score,sorted_sentences[i+3].sentence_score)    
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'main/emotion_check.html')
        
        
        




class ExpressionsTestCase(TestCase):

    def test_expressions_func(self):
        # result = 10+1
        # self.assertEqual(result, 1)
        sentence = "WOW i am so happy :)"
        sad_expressions = [":(", ":'(", ":-(", ":'-(", "=("]
        happy_expressions = [":)", ":-)", ":D", "=)", ":]", ":>", ":^)"]
        """Check edge cases of sentences"""
        self.assertEqual(find_expressions(sentence, sad_expressions, happy_expressions), 1)


