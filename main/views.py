from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import Emotion_Search
from . import emotion_check
from .models import SearchQ, ImportantVars, Sentence, TrainData
import datetime
from LoveHateGame.train import add_pos_neg_sens
import datetime



# def check_today_training(latest_classifier):
#         try:
#                 train_date = ImportantVars.objects.filter(purpose="last_trained_date")[0]
#         except IndexError:
#                 train.train_today(latest_classifier)
#                 t = ImportantVars(date=datetime.date.today(), purpose="last_trained_date")
#                 t.save()
#         else:
#                 if train_date.date != datetime.date.today():
#                         train.train_today()
#                         train_date.date = datetime.date.today()
#                         train_date.save()
                        
               
def get_pos_neg_sens(search: SearchQ):
        all_sens = search.most_positive.all() | search.most_negative.all()
        sorted_sens = sorted(all_sens, key=lambda tup: tup.sentence_score, reverse=True)
        sorted_sens[3:6] = sorted_sens[3:6][::-1]
        return sorted_sens

def get_training_data():
        max_answers =  ImportantVars.objects.get(purpose="max answers").value
        positive_data = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__gte = 2)
        positive_data = list(positive_data.values_list('post_title',flat=True))
        negative_data = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__lte = -2)
        negative_data = list(negative_data.values_list('post_title',flat=True))
        return positive_data, negative_data
        

def home(request):
        
       
        if request.GET.get("search_but"):
                emot_search = Emotion_Search(request.GET)
                if emot_search.is_valid():
                        query = emot_search.cleaned_data["search_query"]
                        if len(list(SearchQ.objects.filter(query=query))) > 0:
                                last_search = list(SearchQ.objects.filter(query=query))[len(list(SearchQ.objects.filter(query=query)))-2] 
                                sentences = get_pos_neg_sens(last_search)
                                return render(request, "main/emotion_check.html", {"emot_search": emot_search, "score" : last_search.score, "sentences" : sentences})
                        else:
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
        
        score, most_positive, most_negative = emotion_check.main(query)
        search_obj = SearchQ.objects.filter(id=id)[0]
        if score is not None:
                search_obj.score = score
        else:
                score = None
        search_obj.date = datetime.datetime.now()
        
        # for sentence in most_positive:
        #         if len(search_obj.most_positive.all()) < 3:
        #                 sen = Sentence(sentence=sentence[0], sentence_score=round(sentence[1],2))
        #                 sen.save()
        #                 search_obj.most_positive.add(sen)
        # for sentence in most_negative:
        #         if len(search_obj.most_negative.all()) < 3:
        #                 sen = Sentence(sentence=sentence[0], sentence_score=round(sentence[1],2))
        #                 sen.save()
        #                 search_obj.most_negative.add(sen)
                
        add_pos_neg_sens(search_obj, most_positive+most_negative)
        
        search_obj.save()
        sentences = get_pos_neg_sens(search_obj)

        return render(request, "main/emotion_check.html", {"query": query, "emot_search": emot_search, "score" : score, "sentences" : sentences})
        
        

def search_requests(request):
        user_id = request.user.id
        searches = SearchQ.objects.filter(user_id=user_id)
        rev_searches = list(searches)
        rev_searches.reverse()
        return render(request, "main/search_requests.html", {"searches": rev_searches, "username": request.user.username, "logged_in" : request.user.is_authenticated})

        
        

