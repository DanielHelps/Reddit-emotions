from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import Emotion_Search
from . import emotion_check
from .models import SearchQ

def home(request):
        if request.GET.get("search_but"):
                emot_search = Emotion_Search(request.GET)
                if emot_search.is_valid():
                        query = emot_search.cleaned_data["search_query"]
                        t = SearchQ(query=query)
                        t.save()
                        if t.user_id is not None:
                                request.user.SearchQ.add(t)
                        return HttpResponseRedirect(f"search={query}/", {"search_query" : query})
                else:                        
                        return HttpResponse("Problem, go back!")
        else:
                emot_search = Emotion_Search()
                return render(request, "main/home.html", {"emot_search": emot_search})
                


def emotion_check_view(request, query):
        emot_search = Emotion_Search()
        (score, common_subs) = emotion_check.main(query)
        return render(request, "main/emotion_check.html", {"emot_search": emot_search, "score" : score, "common_subs": common_subs})
        # return HttpResponse(score)
        

