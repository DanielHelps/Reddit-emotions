# Create your tasks here
from lib2to3.pgen2.pgen import generate_grammar
from celery import shared_task
from celery import Celery
import datetime
from main.emotion_check import get_random_post
from main.models import TrainData, TrainIps, ImportantVars
from django.db.models import Q
from main.classifier_functions import main_training
from .train import top_searches_train
import os

# app = Celery('tasks', broker='rediss://:p9fbece7c880409dd7caea59b72470c1e589d106ef280492efe3a7c544bdc3244@ec2-34-251-208-252.eu-west-1.compute.amazonaws.com:27030')
app = Celery('tasks', broker=os.environ['REDIS_URL'])

def get_client_ip(x_forwarded_for: str, REMOTE_ADDR: str) -> str:
    """receives information from response and returns IP address of the computer 
    with the request

    Args:
        x_forwarded_for (str): response.META["x_forwarded_for"]
        REMOTE_ADDR (str): remote address of the computer accessing this function

    Returns:
        str: A string of the IP of the computer requesting the information 
    """    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = REMOTE_ADDR
    return ip

@shared_task
def get_next_post_update(x_forwarded_for: str, REMOTE_ADDR: str, current_train_post: str) -> str:
    """Gets the next post to display in the "train" section

    Args:
        x_forwarded_for (str): string the includes the real client's Ip + proxy IPs
        REMOTE_ADDR (str): response.META["REMOTE_ADDR"] - IP of the client accessing this function (if not accessing through a proxy IP)
        current_train_post (str): string of the currently displaying train post
        max_answers (int, optional): Max allowed answers for a train post. Only presents posts with less than this amount.
        If no posts with less amount of this exists, creates a new random post. Defaults to ImportantVars.objects.get(purpose="max answers").value.

    Returns:
        post_title, author, subreddit of next post
    """
    ip_str = get_client_ip(x_forwarded_for, REMOTE_ADDR)
    
    try:
        max_answers = ImportantVars.objects.get(purpose="max answers").value
    except:
        max_answers = 3
    
    try:
        if 'ip_obj' not in locals():
            try:
                ip_obj = TrainIps.objects.get(ip=ip_str)
            except:
                ip_obj = TrainIps(ip=ip_str)
                ip_obj.save()
        # Reminder to delete print statements
        print(f"Current train post: {current_train_post}")
        # Search for the next train post in the database that fulfills the following requirements -
        # - IP of client accessing the function did not already answer this train post
        # - The post was answered less than "max_answers" amount of times (default 3)
        # - The post title is NOT the title of the current train post being displayed
        post = TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers)[1]
        # post = TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers)[0]
        print("1111111111111111111111")
        # print(post.post_title, post.author, post.subreddit)
        return post.post_title, post.author, post.subreddit
    except: 
        #If next train post does not exist in database, create one by getting a random post from reddit and push it to database
        train_post, author, subreddit = get_random_post()
        new_post = TrainData(post_title=train_post, author=author, subreddit=subreddit, date=datetime.datetime.now())
        new_post.save()
        print("2222222222222222222222")
        print(new_post.post_title, new_post.author, new_post.subreddit )
        print(f"number of next posts: {len(TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers))}")
        # Already create the next train post so it will be immediately avaliable
        if len(TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=current_train_post), times_answered__lt = max_answers)) < 2:
            extra_train_post, extra_author, extra_subreddit = get_random_post()
            extra_new_post = TrainData(post_title=extra_train_post, author=extra_author, subreddit=extra_subreddit, date=datetime.datetime.now())
            extra_new_post.save()
        
        return new_post.post_title, new_post.author, new_post.subreddit 

@shared_task
def weekly_training():
    """performs the weekly training of the classifier using the extra train data.
    Positive data used = only train sentences that 3 people answered, with score of 2/3 or 3/3.
    Negative data used = only train sentences that 3 people answered, with score of -2/3 or -3/3.
    """    
    max_answers = ImportantVars.objects.get(purpose="max answers").value
    extra_pos = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__gte = 2)
    extra_pos = list(extra_pos.values_list('post_title', flat=True))
    extra_neg = TrainData.objects.filter(times_answered__gte = max_answers, positive_score__lte = -2)
    extra_neg = list(extra_neg.values_list('post_title', flat=True))
    main_training(extra_pos,extra_neg)
    
@shared_task
def daily_training():
    """Performs the daily training - adding top 20 google searches of the day to the scores database
    """    
    try:
        train_day = ImportantVars.objects.filter(purpose="last_trained_date")[0]
    except IndexError: # If train_day variable does not exists (maybe deleted, or first training session)
        top_searches_train()
        t = ImportantVars(date=datetime.date.today(), purpose="last_trained_date")
        t.save()
    else:
        if train_day.date != datetime.date.today():
            top_searches_train()
            train_day.date = datetime.date.today()
            train_day.save()