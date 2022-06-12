from pytrends.request import TrendReq
from main.models import SearchQ
# from django.apps import apps
# MyModel1 = apps.get_model('main', 'SearchQ')
import datetime
from main import emotion_check

global train_day
train_day = 0

def train_today():
    global train_day
    if train_day != datetime.datetime.date(datetime.datetime.now()):
        train_day = datetime.datetime.date(datetime.datetime.now())
        pytrends = TrendReq(hl='en-US')
        today_trends = pytrends.trending_searches()
        date_today = datetime.datetime.date(datetime.datetime.now())
        for item in today_trends.loc[:,0]:
            print(item)
            if list(SearchQ.objects.filter(query=item, date=date_today)) == []:
                scores = emotion_check.main(item)
                if  scores is not None:
                    search_obj = SearchQ(query=item, score=int(list(scores)[0]), date = date_today)        
                    search_obj.save()
            pass