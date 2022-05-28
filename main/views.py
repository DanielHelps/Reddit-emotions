from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import Emotion_Search
from . import emotion_check
from .models import SearchQ
import datetime
from LoveHateGame import train


def home(request):
        train.train_today()
        if request.GET.get("search_but"):
                emot_search = Emotion_Search(request.GET)
                if emot_search.is_valid():
                        query = emot_search.cleaned_data["search_query"]
                        t = SearchQ(query=query)
                        t.save()
                        if request.user.is_authenticated:
                                request.user.logged_user.add(t)
                        return HttpResponseRedirect(f"search={query}/{t.id}")
                else:                        
                        return HttpResponse("Problem, go back!")
        else:
                emot_search = Emotion_Search()
                return render(request, "main/home.html", {"emot_search": emot_search})
                


def emotion_check_view(request, query, id):
        emot_search = Emotion_Search()
        # (scores, common_subs) = emotion_check.main(query)
        if len(list(SearchQ.objects.filter(query=query))) > 1:
                last_search = list(SearchQ.objects.filter(query=query))[len(list(SearchQ.objects.filter(query=query)))-2] 
                # days_difference = (last_search.date - datetime.datetime.now()).days
                # if abs(days_difference) < 7:
                return render(request, "main/emotion_check.html", {"emot_search": emot_search, "score" : last_search.score})
        scores = emotion_check.main(query)
        search_obj = SearchQ.objects.filter(id=id)[0]
        for score in scores: search_obj.score = score
        search_obj.date = datetime.datetime.now()
        search_obj.save()
        # return render(request, "main/emotion_check.html", {"emot_search": emot_search, "score" : score, "common_subs": common_subs})
        return render(request, "main/emotion_check.html", {"emot_search": emot_search, "score" : score})
        
        

def search_requests(request):
        user_id = request.user.id
        searches = SearchQ.objects.filter(user_id=user_id)
        rev_searches = list(searches)
        rev_searches.reverse()
        return render(request, "main/search_requests.html", {"searches": rev_searches, "username": request.user.username, "logged_in" : request.user.is_authenticated})

        
        

