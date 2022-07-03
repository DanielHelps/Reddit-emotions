from pytrends.request import TrendReq
from main.models import SearchQ, Classifier, ImportantVars, Sentence
import datetime
from main import emotion_check


def add_pos_neg_sens(search_obj, sentences):
        for sentence in sentences[0:3]:
                if len(search_obj.most_positive.all()) < 3:
                        sen = Sentence(sentence=sentence[0], sentence_score=round(sentence[1],2))
                        sen.save()
                        search_obj.most_positive.add(sen)
        for sentence in sentences[3:6]:
                if len(search_obj.most_negative.all()) < 3:
                        sen = Sentence(sentence=sentence[0], sentence_score=round(sentence[1],2))
                        sen.save()
                        search_obj.most_negative.add(sen)


def top_searches_train():
    """Fetches the top 20 google searches of the day and adds them (with scores) to the database
    """    
    pytrends = TrendReq(hl='en-US')
    today_trends = pytrends.trending_searches()
    date_today = datetime.datetime.date(datetime.datetime.now())
    for item in today_trends.loc[:,0]:
        print(item)
        if list(SearchQ.objects.filter(query=item, date=date_today)) == []:
            scores, most_positive, most_negative = emotion_check.main(item)
            if  scores[0] is not None:
                search_obj = SearchQ(query=item, score=int(list(scores)[0]), date = date_today)        
                add_pos_neg_sens(search_obj, most_positive+most_negative)
                search_obj.save()
        pass

# def daily_training():
#     try:
#         train_day = ImportantVars.objects.filter(purpose="last_trained_date")[0]
#     except IndexError:
#         top_searches_train()
#         t = ImportantVars(date=datetime.date.today(), purpose="last_trained_date")
#         t.save()
#     else:
#         if train_day.date != datetime.date.today():
#             top_searches_train()
#             train_day.date = datetime.date.today()
#             train_day.save()
