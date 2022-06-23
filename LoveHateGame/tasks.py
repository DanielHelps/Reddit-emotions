# Create your tasks here
from celery import shared_task
from celery import Celery
import time
import datetime
from main.emotion_check import get_random_post
from main.models import TrainData, TrainIps
from django.db.models import Q
# global train_post
import time

app = Celery('tasks', broker='rediss://:pba041f448e29eb5ae3008eb717539810314741333e3b7fac3b68f225554b377d@ec2-52-50-219-146.eu-west-1.compute.amazonaws.com:7740')

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
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def get_training_post(x_forwarded_for, REMOTE_ADDR, train_but, method, train_post):
    # global train_post
    max_answers = 3
    ip_str = get_client_ip(x_forwarded_for, REMOTE_ADDR)
    print("DONNNNNNNNNNNNNNNNNNNNNNNNNE")
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


def get_next_post(ip_str, max_answers, next_train_post, next_author, next_subreddit):
    try:
        if 'ip_obj' not in locals():
            ip_obj = TrainIps.objects.get(ip=ip_str)
        # Searching for existing post with <3 answers and without the current IP
        post = TrainData.objects.filter(~Q(train_ips=ip_obj), times_answered__lt = max_answers)[0]
        return post
    except:
        train_post, author, subreddit = next_train_post, next_author, next_subreddit
        new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
        new_post.save()
        return new_post
    
    
@shared_task
def get_async_next_post(ip_str, max_answers):
    # try:
    #     if 'ip_obj' not in locals():
    #         ip_obj = TrainIps.objects.get(ip=ip_str)
    #     # print(TrainData.train_ips.through.objects.all())
    #     post = TrainData.objects.filter(~Q(train_ips=ip_obj), times_answered__lt = max_answers)[0]
    # except:
    rand_train_post, rand_author, rand_subreddit = get_random_post()
    post = get_next_post(ip_str, max_answers, rand_train_post, rand_author, rand_subreddit)
    return post.post_title, post.author, post.subreddit
    # new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
    # new_post.save()