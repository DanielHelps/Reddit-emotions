from pytrends.request import TrendReq
from main.models import SearchQ
# from django.apps import apps
# MyModel1 = apps.get_model('main', 'SearchQ')
import datetime
from main import emotion_check

def train_today():
    
    pytrends = TrendReq(hl='en-US')
    today_trends = pytrends.trending_searches()
    date_today = datetime.datetime.date(datetime.datetime.now())
    for item in today_trends.loc[:,0]:
        print(item)
        if SearchQ.objects.filter(query=item, date=date_today) is None and scores is not None:
            scores = emotion_check.main(item)
            search_obj = SearchQ(query=item, score=list(scores)[0], date = date_today)        
            search_obj.save()
        pass