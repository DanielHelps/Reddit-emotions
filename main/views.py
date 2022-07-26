from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import Emotion_Search
from . import emotion_check
from .models import SearchQ, ImportantVars, TrainData
import datetime
from LoveHateGame.train import add_pos_neg_sens
import datetime
import re


def get_pos_neg_sens(search: SearchQ):
        """Receives a search query and returns the most negative and most positive sentences

        Args:
            search (SearchQ): A searchQ object

        Returns:
            list: sentences list with: [0:3] - most positive sentences, [3:6] - most negative sentences
        """        
        all_sens = search.most_positive.all() | search.most_negative.all()
        sorted_sens = sorted(all_sens, key=lambda tup: tup.sentence_score, reverse=True)
        # Negative sentences need to be sorted from lowest score to highest, so need to flip sort
        sorted_sens[3:6] = sorted_sens[3:6][::-1]
        return sorted_sens

def get_training_data():
        """creates a list of the positive sentences and negative sentences for weekly classifier training

        Returns:
            2 lists: positive sentences list and negative sentences list
        """        
        max_answers =  ImportantVars.objects.get(purpose="max answers").value
        # Positive sentence = sentence that was classified "max answers" of times (3 default) and has a score of 2 at least (2 positive + 1 neutral or 3 positive)
        positive_data = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__gte = 2)
        # Negative sentence = sentence that was classified "max answers" of times (3 default) and has a score of -2 at least (2 negative + 1 neutral or 3 negative)
        positive_data = list(positive_data.values_list('post_title',flat=True))
        negative_data = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__lte = -2)
        negative_data = list(negative_data.values_list('post_title',flat=True))
        return positive_data, negative_data
        

def home(request):          
        try:
                print(request.META['HTTP_REFERER'])
                referral = "here"
        except:
                referral = "other"
        if request.GET.get("search_but"):
                # User pressed the calculate button
                emot_search = Emotion_Search(request.GET)
                if emot_search.is_valid():
                        query = emot_search.cleaned_data["search_query"]
                        # If the search query exists already in the database
                        if len(list(SearchQ.objects.filter(query=query))) > 0:
                                last_search = list(SearchQ.objects.filter(query=query))[len(list(SearchQ.objects.filter(query=query)))-2] 
                                sentences = get_pos_neg_sens(last_search)
                                return render(request, "main/emotion_check.html", {"emot_search": emot_search, "score" : last_search.score, "sentences" : sentences, "referral": referral})
                        else:
                                # Create a Search Query object
                                t = SearchQ(query=query)
                                t.save()
                                if request.user.is_authenticated:
                                        request.user.logged_user.add(t)
                                return HttpResponseRedirect(f"search={query}/{t.id}")
                else:                        
                        return HttpResponse("Problem, go back!")
        else:
                # User just entered the page
                
                emot_search = Emotion_Search()
                return render(request, "main/home.html", {"emot_search": emot_search, "referral": referral})
                


def emotion_check_view(request, query, id):
        emot_search = Emotion_Search()
        # Perform classification of search term
        score, most_positive, most_negative = emotion_check.main_check(query)
        # Get the SearchQ object that was just created
        search_obj = SearchQ.objects.filter(id=id)[0]
        if score is not None:
                search_obj.score = score
        else:
                score = None
        search_obj.date = datetime.datetime.now()
        add_pos_neg_sens(search_obj, most_positive+most_negative)
        
        search_obj.save()
        sentences = get_pos_neg_sens(search_obj)
        try:
                print(request.META['HTTP_REFERER'])
                referral = "here"
        except:
                referral = "other"
        return render(request, "main/emotion_check.html", {"query": query, "emot_search": emot_search, "score" : score, "sentences" : sentences, "referral": referral})
        
        

def search_requests(request):
        user_id = request.user.id
        # Get all the searches for this specific user
        searches = SearchQ.objects.filter(user_id=user_id)
        rev_searches = list(searches)
        # Reverse in order to show from latest to 
        rev_searches.reverse()
        try:
                print(request.META['HTTP_REFERER'])
                referral = "here"
        except:
                referral = "other"
        return render(request, "main/search_requests.html", {"searches": rev_searches, "username": request.user.username, "logged_in" : request.user.is_authenticated, "referral": referral})

        
        

