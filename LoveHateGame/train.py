from pytrends.request import TrendReq
from main.models import SearchQ, Classifier, ImportantVars
# from django.apps import apps
# MyModel1 = apps.get_model('main', 'SearchQ')
import datetime
from main import emotion_check

def top_searches_train():
    pytrends = TrendReq(hl='en-US')
    today_trends = pytrends.trending_searches()
    date_today = datetime.datetime.date(datetime.datetime.now())
    for item in today_trends.loc[:,0]:
        print(item)
        if list(SearchQ.objects.filter(query=item, date=date_today)) == []:
            scores = emotion_check.main(item)
            if  scores[0] is not None:
                search_obj = SearchQ(query=item, score=int(list(scores)[0]), date = date_today)        
                search_obj.save()
        pass

def daily_training():
    try:
        train_day = ImportantVars.objects.filter(purpose="last_trained_date")[0]
    except IndexError:
        top_searches_train()
        t = ImportantVars(date=datetime.date.today(), purpose="last_trained_date")
        t.save()
    else:
        if train_day.date != datetime.date.today():
            top_searches_train()
            train_day.date = datetime.date.today()
            train_day.save()
