# Create your tasks here
from celery import shared_task
from celery import Celery
import time
import datetime
from main.emotion_check import get_random_post
from main.models import TrainData, TrainIps, ImportantVars
from django.db.models import Q
# global train_post
import time
import requests 
from requests.auth import HTTPBasicAuth
from main.classifier_functions import main_training



app = Celery('tasks', broker='redis://:pba041f448e29eb5ae3008eb717539810314741333e3b7fac3b68f225554b377d@ec2-52-50-219-146.eu-west-1.compute.amazonaws.com:7740')

def get_client_ip(x_forwarded_for, REMOTE_ADDR):
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = REMOTE_ADDR
    return ip


@shared_task
def add(x, y):
    
    time.sleep(3)
    print(x+y)
    # return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def get_training_post(x_forwarded_for, REMOTE_ADDR, train_but, method, train_post):
    # global train_post
    max_answers = ImportantVars.objects.get(purpose="max answers").value
    ip_str = get_client_ip(x_forwarded_for, REMOTE_ADDR)
   
    print(train_post)
    if method == "POST":
        # if "positive" in requ est.POST:
        post = TrainData.objects.filter(post_title=train_post)[0]
        post.times_answered += 1
        post.positive_score += int(train_but)
        

        try:
            ip_obj = TrainIps.objects.get(ip=ip_str)
        except:
            ip_obj = TrainIps(ip=ip_str)
            ip_obj.save()
        post.train_ips.add(ip_obj)
        post.save()

    try:
        if 'ip_obj' not in locals():
            ip_obj = TrainIps.objects.get(ip=ip_str)
        # print(TrainData.train_ips.through.objects.all())
        post = TrainData.objects.filter(~Q(train_ips=ip_obj), times_answered__lt = max_answers)[0]
        train_post = post.post_title
    except:
        train_post, author, subreddit = get_random_post()
        new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
        new_post.save()
    
    print("AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIN")
    print(train_post)
    # else:
    #     train_post = post.post_title
    #     author = post.author
    #     subreddit = post.subreddit
    
    # return train_post, author, subreddit
    # train_post, author, subreddit = get_random_post()
    # new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
    # new_post.save()

@shared_task
def get_oauth():
    auth = HTTPBasicAuth('vw-fkwBL0vnxGZ5Ofm5VKw', 'ULkWg9VlM0ObIqI1nDdtdVsFsmTG5Q')
    # auth = HTTPBasicAuth('classified', 'classified')

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': 'checking_sentiment',
            'password': '8S(pM;,E]crQQ{9:'}

    # data =  {'grant_type': 'password',
    #         'username': 'classified',
    #         'password': 'classified'}

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'sentiment_analysis_bot'}
    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    return headers

@shared_task
def get_random_post():
    headers = get_oauth()
    # print(headers)
    # headers = {'User-Agent': 'sentiment_analysis_bot', 'Authorization': 'bearer 1764285820863-nZZolhuiCOPnXBcXtpQlmh30Z9IUCA'}
    # try:
    res = requests.get("https://oauth.reddit.com/random", headers= headers)
    # except:
        # headers = get_oauth()
    # print(headers)
    headers = {'User-Agent': 'sentiment_analysis_bot', 'Authorization': 'bearer 1764285820863-nZZolhuiCOPnXBcXtpQlmh30Z9IUCA'}
    post_title = res.json()[0]['data']['children'][0]['data']['title']
    author = res.json()[0]['data']['children'][0]['data']['author']
    subreddit = res.json()[0]['data']['children'][0]['data']['subreddit_name_prefixed']
    # *****************
    return post_title, author, subreddit

@shared_task
def save_random_post():
    post_title, author, subreddit = get_random_post()
    while True:
        try:
            TrainIps.objects.get(post_title=post_title)
        except:
            break
        
    new_post = TrainData(post_title=post_title, author=author, subreddit=subreddit, date=datetime.datetime.now())
    new_post.save()

@shared_task
def get_next_post_update(x_forwarded_for, REMOTE_ADDR, current_train_post, max_answers=3):
    ip_str = get_client_ip(x_forwarded_for, REMOTE_ADDR)
    
    try:
        if 'ip_obj' not in locals():
            try:
                ip_obj = TrainIps.objects.get(ip=ip_str)
            except:
                ip_obj = TrainIps(ip=ip_str)
                ip_obj.save()
        # print(TrainData.train_ips.through.objects.all())
        print(f"Current train post: {current_train_post}")
        post = TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers)[1]
        print("1111111111111111111111")
        print(post.post_title, post.author, post.subreddit)
        return post.post_title, post.author, post.subreddit
    except:
        train_post, author, subreddit = get_random_post()
        new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
        new_post.save()
        print("2222222222222222222222")
        print(new_post.post_title, new_post.author, new_post.subreddit )
        print(f"number of next posts: {len(TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers))}")
        if len(TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers)) < 2:
            extra_train_post, extra_author, extra_subreddit = get_random_post()
            extra_new_post = TrainData(post_title=extra_train_post, author=extra_author, subreddit=extra_subreddit, date=datetime.datetime.now())
            extra_new_post.save()
        
        return new_post.post_title, new_post.author, new_post.subreddit 

@shared_task
def get_next_post(ip_str, max_answers, next_train_post, next_author, next_subreddit):
    try:
        if 'ip_obj' not in locals():
            ip_obj = TrainIps.objects.get(ip=ip_str)
        # Searching for existing post with <3 answers and without the current IP
        post = TrainData.objects.filter(~Q(train_ips=ip_obj), times_answered__lt = max_answers)[1]
        print("1111111111111111111111")
        return post.post_title, post.author, post.subreddit
    except:
        train_post, author, subreddit = next_train_post, next_author, next_subreddit
        new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
        new_post.save()
        print("2222222222222222222222")
        return new_post.post_title, new_post.author, new_post.subreddit    
    
@shared_task
def get_async_next_post(ip_str, max_answers):
    
    # res = get_random_post.delay()
    
    ######################
    auth = HTTPBasicAuth('vw-fkwBL0vnxGZ5Ofm5VKw', 'ULkWg9VlM0ObIqI1nDdtdVsFsmTG5Q')
    # auth = HTTPBasicAuth('classified', 'classified')

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': 'checking_sentiment',
            'password': '8S(pM;,E]crQQ{9:'}

    # data =  {'grant_type': 'password',
    #         'username': 'classified',
    #         'password': 'classified'}

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'sentiment_analysis_bot'}
    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
    
    res = requests.get("https://oauth.reddit.com/random", headers=headers)
    rand_train_post = res.json()[0]['data']['children'][0]['data']['title']
    rand_author = res.json()[0]['data']['children'][0]['data']['author']
    rand_subreddit = res.json()[0]['data']['children'][0]['data']['subreddit_name_prefixed']
    ######################
    
    
    # rand_train_post, rand_author, rand_subreddit = res.get()
    post = get_next_post(ip_str, max_answers, rand_train_post, rand_author, rand_subreddit)
    return post.post_title, post.author, post.subreddit
    
    
@shared_task
def weekly_training(max_answers):
    extra_pos = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__gte = 2)
    extra_pos = list(extra_pos.values_list('post_title', flat=True))
    extra_neg = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__lte = -2)
    extra_neg = list(extra_neg.values_list('post_title', flat=True))
    main_training(extra_pos,extra_neg)