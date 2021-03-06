# from urllib import response
from django.test import TestCase, Client
from django.urls import reverse
from .forms import Emotion_Search
from .models import SearchQ, Sentence, Classifier, top_100
from .views import get_pos_neg_sens
from .emotion_check import *
from .classifier_functions import *
import pickle
import datetime
from nltk.sentiment import SentimentIntensityAnalyzer

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
        self.sentence_list_positive = [("score 0.2", 0.2),
                         ("score 0.51", 0.51), 
                         ("score 0.9", 0.9)]
        self.sentence_list_negative = [("score -0.7", -0.7), 
                         ("score -0.4", -0.4), 
                         ("score -0.2", -0.2)]
        with open('classifier.pickle', 'rb') as f:
            classifier = pickle.load(f)
            a = Classifier.objects.create(classifier_obj=classifier, classifier_date=datetime.datetime.now())
            a.save()
        with open('top_100_pos.pickle', 'rb') as f:
            top_100_pos = pickle.load(f)
            b = top_100.objects.create(top_obj=top_100_pos, pos_date=datetime.datetime.now())
            b.save()
        with open('top_100_neg.pickle', 'rb') as f:
            top_100_neg = pickle.load(f)
            c = top_100.objects.create(top_obj=top_100_neg, neg_date=datetime.datetime.now())
            c.save()
        self.sia = SentimentIntensityAnalyzer()
        # with open('classifier.pickle', 'rb') as f:
        #     classifier = pickle.load(f)
        
    
    # def test_import_top_100(self):
    #     #WARNING - A LONG TEST (~30s) BECAUSE OF API CALLS AND CLASSIFIER CREATION
    #     top_100_negative, top_100_positive  = import_top_100()
    #     self.assertEqual(len(top_100_negative),100)
    #     self.assertEqual(len(top_100_positive),100)
    
    def test_check_sentence_list(self):
        check_sentence_1 = ("sentence to check score 0.1", 0.1)
        check_sentence_2 = ("sentence to check score 0.5", 0.5)
        check_sentence_3 = ("sentence to check score 0.99", 0.99)
        check_sentence_4 = ("sentence to check score -0.1", -0.1)
        check_sentence_5 = ("sentence to check score -0.3", -0.3)
        check_sentence_6 = ("sentence to check score -0.9", -0.9)
        
        
        self.assertNotIn(check_sentence_1, check_sentence_list("positive", self.sentence_list_positive, check_sentence_1))
        self.assertNotIn(check_sentence_1, check_sentence_list("negative", self.sentence_list_negative, check_sentence_1))
        self.assertIn(check_sentence_2, check_sentence_list("positive", self.sentence_list_positive, check_sentence_2))
        self.assertNotIn(check_sentence_2, check_sentence_list("negative", self.sentence_list_negative, check_sentence_2))
        self.assertIn(check_sentence_3, check_sentence_list("positive", self.sentence_list_positive, check_sentence_3))
        self.assertNotIn(check_sentence_3, check_sentence_list("negative", self.sentence_list_negative, check_sentence_3))
        self.assertNotIn(check_sentence_4, check_sentence_list("positive", self.sentence_list_positive, check_sentence_4))
        self.assertNotIn(check_sentence_4, check_sentence_list("negative", self.sentence_list_negative, check_sentence_4))
        self.assertNotIn(check_sentence_5, check_sentence_list("positive", self.sentence_list_positive, check_sentence_5))
        self.assertIn(check_sentence_5, check_sentence_list("negative", self.sentence_list_negative, check_sentence_5))
        self.assertNotIn(check_sentence_6, check_sentence_list("positive", self.sentence_list_positive, check_sentence_6))
        self.assertIn(check_sentence_6, check_sentence_list("negative", self.sentence_list_negative, check_sentence_6))
        
    
            
    def test_text_classification(self):
        happy_sentence = "happy love beautiful"
        sad_sentence = "horror death war"
        neutral_sentence = "neutral sentence"
        count = 0
        pos_count = 0
        top_100_neg, top_100_pos  = import_top_100()
        
        new_count, new_pos_count, new_pos_sens, new_neg_sens = classify_text(happy_sentence, 
                        top_100_neg,
                        top_100_pos,
                        self.sia, count,
                        pos_count,
                        self.sentence_list_positive,
                        self.sentence_list_negative)
        self.assertGreater(new_count, count)
        self.assertGreater(new_pos_count, pos_count)
        self.assertNotIn(happy_sentence, [x[0] for x in new_neg_sens])
        self.assertIn(happy_sentence, [x[0] for x in new_pos_sens])

        new_count, new_pos_count, new_pos_sens, new_neg_sens = classify_text(sad_sentence, 
                        top_100_neg,
                        top_100_pos,
                        self.sia, count,
                        pos_count,
                        self.sentence_list_positive,
                        self.sentence_list_negative)
        self.assertGreater(new_count, count)
        self.assertEqual(new_pos_count, pos_count)
        self.assertNotIn(sad_sentence, [x[0] for x in new_pos_sens])
        self.assertIn(sad_sentence, [x[0] for x in new_neg_sens])
        
        new_count, new_pos_count, new_pos_sens, new_neg_sens = classify_text(neutral_sentence, 
                        top_100_neg,
                        top_100_pos,
                        self.sia, count,
                        pos_count,
                        self.sentence_list_positive,
                        self.sentence_list_negative)
        self.assertEqual(new_count, count)
        self.assertEqual(new_pos_count, pos_count)
        self.assertNotIn(neutral_sentence, [x[0] for x in new_pos_sens])
        self.assertNotIn(neutral_sentence, [x[0] for x in new_neg_sens])
        
    def test_random_post(self):
        title, author, subreddit = get_random_post()
        
        self.assertRegex(title,'.+')
        self.assertRegex(author,'.+')
        self.assertRegex(subreddit,'r/.+')
        
        print(title, author, subreddit)
        
    # def test_main_emotion_check(self):
    # #     #WARNING - A LONG TEST (~20s) BECAUSE OF API CALLS AND CLASSIFIER CREATION

    #     queries = ['death', 'neutral', 'beautiful', '', 'dsfgdglkhsoqiewrh312', 2]
        
    #     for i, query in enumerate(queries):
    #         if i <= 2:
    #             score, most_pos, most_neg = main_check(query)
    #             self.assertEqual(len(most_pos),3)
    #             self.assertEqual(len(most_neg),3)
    #             # self.assertEqual(type(score),int)
    #             self.assertRegex(str(score), '\d\d\.\d\d|\d\.\d\d')
    #         else:
    #             self.assertEqual(main_check(query), (None, [], []))
        
            
        

# -------------------------------------------------------------------------

class ClassifierFunctionsTestCase(TestCase):
    def setUp(self):
        with open('top_100_pos.pickle', 'rb') as f:
            top_100_pos = pickle.load(f)
            b = top_100.objects.create(top_obj=top_100_pos, pos_date=datetime.datetime.now())
            b.save()
        with open('top_100_neg.pickle', 'rb') as f:
            top_100_neg = pickle.load(f)
            c = top_100.objects.create(top_obj=top_100_neg, neg_date=datetime.datetime.now())
            c.save()
        self.sia = SentimentIntensityAnalyzer()
    
    def test_extracting_feature(self):
        text1 = ""
        text2 = "love"
        text3 = "death"
        text4 = "12!@dsao0)9(+-*/"
        pos_100 = top_100.objects.latest('pos_date').top_obj
        neg_100 = top_100.objects.latest('neg_date').top_obj
        features1 = extract_features(text1, pos_100, neg_100, self.sia)
        features2 = extract_features(text2, pos_100, neg_100, self.sia)
        features3 = extract_features(text3, pos_100, neg_100, self.sia)
        features4 = extract_features(text4, pos_100, neg_100, self.sia)
        # {'mean_compound': 0.0, 'mean_positive': 0.0, 'pos_wordcount': 0}
        
        self.assertIn('mean_compound',features1)
        self.assertEqual(features1['mean_compound'], 0.0)
        self.assertIn('mean_positive',features1)
        self.assertEqual(features1['mean_positive'], 0.0)
        self.assertIn('pos_wordcount',features1)
        self.assertEqual(features1['pos_wordcount'], 0)
        
        self.assertIn('mean_compound',features2)
        self.assertGreater(features2['mean_compound'], 0.0)
        self.assertIn('mean_positive',features2)
        self.assertGreater(features2['mean_positive'], 0.0)
        self.assertIn('pos_wordcount',features2)
        
        self.assertIn('mean_compound',features3)
        self.assertLess(features3['mean_compound'], 0.0)
        self.assertIn('mean_positive',features3)
        self.assertEqual(features3['mean_positive'], 0.0)
        self.assertIn('pos_wordcount',features3)
        self.assertEqual(features3['pos_wordcount'], 0)
        
        self.assertIn('mean_compound',features4)
        self.assertEqual(features4['mean_compound'], 0.0)
        self.assertIn('mean_positive',features4)
        self.assertEqual(features4['mean_positive'], 0.0)
        self.assertIn('pos_wordcount',features4)
        self.assertEqual(features4['pos_wordcount'], 0)
        
    def test_remove_tweet_unwanted(self):
        tweet1 = 'nice one @daniel '
        tweet2 = 'nice o n e @daniel '
        tweet3 = 'https://www.google.com/  nice'
        tweet4 = 'nice https://www.google.com/@daniel nice'
        
        self.assertEqual(remove_tweet_unwanted(tweet1),'nice one  ')
        self.assertEqual(remove_tweet_unwanted(tweet2),'nice  ')
        self.assertEqual(remove_tweet_unwanted(tweet3),'  nice')
        self.assertEqual(remove_tweet_unwanted(tweet4),'nice  nice')
    
    def test_expressions_func(self):
        sentence = "WOW i am so happy :)"
        sad_expressions = [":(", ":'(", ":-(", ":'-(", "=("]
        happy_expressions = [":)", ":-)", ":D", "=)", ":]", ":>", ":^)"]
        self.assertEqual(find_expressions(sentence, sad_expressions, happy_expressions), 1)