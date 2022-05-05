from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import Emotion_Search
from . import emotion_check

def home(request):
        emot_search = Emotion_Search(request.GET)
        if request.GET.get("save_but"):
                if emot_search.is_valid():
                        query = emot_search.cleaned_data["search_query"]
                        return HttpResponseRedirect(f"search={query}/", {"search_query" : query})
                        # return HttpResponse("GOOOD")
                else:                        
                        return HttpResponse("Problem, go back!")
        else:
                return render(request, "main/home.html", {"emot_search": emot_search})
                


def emotion_check_view(request, query):
        # emot_search = Emotion_Search()
        # emotion_check.main()
        # return render(request, "main/emotion_check.html", {"search_query" : query})
        return HttpResponse(query)
        

