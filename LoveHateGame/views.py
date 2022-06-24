from django.shortcuts import render
from main.emotion_check import get_random_post
from main.models import TrainData, TrainIps
from django.db.models import Q
import datetime
import time
from .tasks import add, get_training_post, get_async_next_post, get_next_post_update
# Create your views here.

global train_post, next_train_post, next_author, next_subreddit
train_post = None
next_train_post = None
next_author = None
next_subreddit = None

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def train_emot_click(request, ip_str):
    post = TrainData.objects.filter(post_title=train_post)[0]
    post.times_answered += 1
    post.positive_score += int(request.POST.get("train_button"))
    try:
        ip_obj = TrainIps.objects.get(ip=ip_str)
    except:
        ip_obj = TrainIps(ip=ip_str)
        ip_obj.save()
    post.train_ips.add(ip_obj)
    post.save()


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


def train(request):
    global train_post, next_train_post, next_author, next_subreddit
    ip_str = get_client_ip(request)
    max_answers = 3
    
    
    # save_random_post.delay() 
    # res = get_async_next_post.delay(ip_str, max_answers)
    
    if request.method == "POST":
        train_emot_click(request, ip_str)
        train_post = next_train_post
        author = next_author
        subreddit = next_subreddit
    else:
        # post = get_next_post(ip_str, max_answers, 'a','b','c')
        train_post, author, subreddit = get_next_post_update(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), current_train_post="None")
        next_train_post, next_author, next_subreddit = get_next_post_update(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), current_train_post=train_post)
    
    ip_obj = TrainIps.objects.get(ip=ip_str)
    # if a
    # while a.state != "SUCCESS":
    #     time.sleep(0.1)
    a = get_next_post_update.delay(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), next_train_post)
    while True:
        try:
            # next_train_post, next_author, next_subreddit = a.get()
            
            next_post = TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=train_post), times_answered__lt = max_answers)[0]
        except:
            while a.state != "SUCCESS":
                time.sleep(0.1)
            continue
        break
    
    
    if request.method == "POST":
        # next_train_post, next_author, next_subreddit = next_post.post_title, next_post.author, next_post.subreddit
        train_post, author, subreddit = next_post.post_title, next_post.author, next_post.subreddit

    # next_post.
    # new_post = res.get()
    # next_train_post, next_author, next_subreddit = res.get()
    
    # if request.method == "GET":
    #     res = get_training_post(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), request.POST.get("train_button"), request.method, train_post)
        
    # else:
    #     res = get_training_post.delay(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), request.POST.get("train_button"), request.method, train_post)
    # #################################
    
    
    
    # if request.method == "POST":
    #     train_emot_click(request, ip_str)

    # next_post = get_next_post(ip_str, max_answers, next_train_post, next_author, next_subreddit)
    # try:
    #     if 'ip_obj' not in locals():
    #         ip_obj = TrainIps.objects.get(ip=ip_str)
    #     # print(TrainData.train_ips.through.objects.all())
    #     post = TrainData.objects.filter(~Q(train_ips=ip_obj), times_answered__lt = max_answers)[0]
    # except:
    # async_random_post(ip_str, max_answers)
        
        # train_post, author, subreddit = get_random_post()
        # ########
        # # author = "sdfsdf"
        # # subreddit = "sdfff"
        # # train_post = str(add.delay(1,10))
        # #########
        # new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
        # new_post.save()
    # else:
        # train_post = post.post_title
        # author = post.author
        # subreddit = post.subreddit
    
    #######################

    
    # train_post = next_post.post_title
    # author = next_post.author
    # subreddit = next_post.subreddit
    # res = get_training_post.delay(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), request.POST.get("train_button"), request.method)
    # train_post, author, subreddit = res.get()
    return render(request, "LoveHateGame/train.html", {"post_title": train_post, "author":author, "subreddit":subreddit})
        
    
