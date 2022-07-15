# from urllib import response
from django.test import TestCase, Client
from .classifier_functions import find_expressions
from django.urls import reverse
from .forms import Emotion_Search
from .models import SearchQ, Sentence
from .views import get_pos_neg_sens
from .emotion_check import *

class HomeViewTestCase(TestCase):
    def setUp(self) -> None:
        self.query = 'test'
        self.client = Client()
        self.home_url = reverse('home')
        self.emote_search = Emotion_Search()
        positive_1 = Sentence.objects.create(sentence="pos1", sentence_score=0.8)
        positive_2 = Sentence.objects.create(sentence="pos2", sentence_score=0.1)
        positive_3 = Sentence.objects.create(sentence="pos3", sentence_score=0.9)
        negative_1 = Sentence.objects.create(sentence="neg1", sentence_score=-0.1)
        negative_2 = Sentence.objects.create(sentence="neg2", sentence_score=-0.7)
        negative_3 = Sentence.objects.create(sentence="neg3", sentence_score=-0.6)
        self.search_obj = SearchQ.objects.create(query=self.query, score=85.0)
        self.search_obj.most_positive.set([positive_1, positive_2, positive_3])
        self.search_obj.most_negative.set([negative_1, negative_2, negative_3])
        self.search_obj.save()
        
    def test_home_no_button_click(self):
        response = self.client.get(self.home_url)
        
        self.assertEquals(response.status_code, 200)
        
    def test_home_button_click_value_invalid(self):
        # If search value is not valid
        response = self.client.get(self.home_url, {
            'search_but':'clicked'
        })
        
        self.assertEqual(str(response.content), "b'Problem, go back!'")
        
    def test_home_button_click_value_valid_not_in_db(self):
        # When value is valid but query doesn't exists in database
        another_query = 'another_test'
        response = self.client.get(self.home_url, {
            'search_but':'clicked',
            'search_query': another_query,
            })
        new_searchQ = SearchQ.objects.get(query=another_query)
        redirect_url_query = response.url.split("/")[0].split("search=")[1]
        redirect_url_query_id = int(response.url.split("/")[1])
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response,'main/emotion_check.html')
        # Checks that redirect url is in the format of "search={search_query}/{search_query.id}"
        self.assertEqual(new_searchQ.id, redirect_url_query_id)
        self.assertEqual(new_searchQ.query, redirect_url_query)
        
        
        
    def test_home_button_click_value_valid_in_db(self):
        # When value is valid and query exists in database
        response = self.client.get(self.home_url, {
            'search_but':'clicked',
            'search_query': self.query
            })
        sorted_sentences = get_pos_neg_sens(self.search_obj)
        
        # checks that get_pos_neg_sens works properly
        self.assertEqual(len(get_pos_neg_sens(self.search_obj)),6)
        for i, sentence in enumerate(sorted_sentences[1:3]):
            self.assertLessEqual(sentence.sentence_score,sorted_sentences[i].sentence_score)    
        for i, sentence in enumerate(sorted_sentences[4:6]):
            self.assertGreaterEqual(sentence.sentence_score,sorted_sentences[i+3].sentence_score)    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'main/emotion_check.html')
        self.assertEqual(response.context["score"], 85.0)
        
        
        
class EmotionCheckViewTestCase(TestCase):
    def setUp(self):
        self.query = 'obama'
        self.client = Client()
        self.search_obj = SearchQ.objects.create(query=self.query)
        self.search_obj.save()
        self.emotion_check_url = reverse('emotion check', kwargs={'query':self.query,
                                                                  'id':self.search_obj.id})

    # def test_emotion_check(self):
    #     # creates a classifier (because none exists) and checks for emotion of query
    #     # WARNING - A LONG TEST (~30s) BECAUSE OF API CALLS AND CLASSIFIER CREATION
    #     response = self.client.get(self.emotion_check_url)
    #     self.assertEqual(response.context['query'], self.query)
    #     self.assertEqual(len(response.context['sentences']),6)
        
        
class SearchRequestsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.search_requests = reverse('search_requests')
        # self.username = 'daniel'
        # self.password1 = 'Asdfslk12102dsf!'
        # self.register = reverse('register')

    
    def test_unregistered_user(self):
        response = self.client.get(self.search_requests)
        self.assertEqual(response.context['searches'],[])
        self.assertEqual(response.context['username'],'')
        self.assertEqual(response.context['logged_in'], False)
        
    # def test_registered_user(self):
    #     self.client.post(self.register, kwargs={'username':self.username,
    #                                             'password1':self.password1})
    #     # print()
    #     response = self.client.get(self.search_requests, data={'response.user.is_authenticated':True})
    #     self.assertEqual(response.context['searches'],[])
    #     self.assertEqual(response.context['username'],'')
    #     self.assertEqual(response.context['logged_in'], False)
    #     self.assertTemplateUsed(response, 'main/search_requests.html')

class EmotionCheckFunctionsTestCase(TestCase):
    def setUp(self):
        pass
    
    def test_import_top_100(self):
        top_100_negative, top_100_positive  = import_top_100()
        self.assertEqual(len(top_100_negative),100)
        


# -------------------------------------------------------------------------

class ExpressionsTestCase(TestCase):

    def test_expressions_func(self):
        # result = 10+1
        # self.assertEqual(result, 1)
        sentence = "WOW i am so happy :)"
        sad_expressions = [":(", ":'(", ":-(", ":'-(", "=("]
        happy_expressions = [":)", ":-)", ":D", "=)", ":]", ":>", ":^)"]
        """Check edge cases of sentences"""
        self.assertEqual(find_expressions(sentence, sad_expressions, happy_expressions), 1)


