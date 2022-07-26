from django.shortcuts import render
from main.models import TrainData, TrainIps, ImportantVars
from django.db.models import Q
import time
from .tasks import get_next_post_update
import datetime

global train_post, next_train_post, next_author, next_subreddit
train_post = None
next_train_post = None
next_author = None
next_subreddit = None

def get_client_ip(request) -> str:
    """A function the finds the client IP

    Args:
        request (Request): A request from the server

    Returns:
        str: string that contains the IP of the client
    """    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # Check if the client is accessing through proxy IP, and take only the real client's IP
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else: # If not accessing through a proxy IP
        ip = request.META.get('REMOTE_ADDR')
    return ip

def train_emot_click(request, ip_str: str):
    """A function that is called after one of the train emotion buttons were clicked. It updates the train sentence
    with the value of the button that was clicked, and links the sentence to the IP of the client so the sentence
    won't appear again for the user

    Args:
        request (request): request object containing the data which button was clicked
        ip_str (str): the IP address of the client
    """    
    post = TrainData.objects.filter(post_title=train_post)[0]
    post.times_answered += 1
    # Add the value of the button that was pressed to the total value:
    # positive = +1, neurtal = 0, negative = -1
    post.positive_score += int(request.POST.get("train_button"))
    try:
        # Link IP to the train sentence
        ip_obj = TrainIps.objects.get(ip=ip_str)
    except:
        # If IP is not in the database
        ip_obj = TrainIps(ip=ip_str)
        ip_obj.save()
    post.train_ips.add(ip_obj)
    post.save()




def train(request):
    global train_post, next_train_post, next_author, next_subreddit
    ip_str = get_client_ip(request)
    try:
        max_answers = ImportantVars.objects.get(purpose="max answers").value
    except:
        a = ImportantVars.objects.create(purpose="max answers", value=3, date = datetime.datetime.date(datetime.datetime.now()))
        a.save()
        max_answers = a.value
    
    if request.method == "POST":
        train_emot_click(request, ip_str)
        # If one of the emotion buttons were pressed, get ready with the next train post
        train_post = next_train_post
        author = next_author
        subreddit = next_subreddit
    else:
        # If just entered the page, get the current and the next train posts
        train_post, author, subreddit = get_next_post_update(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), current_train_post="None")
        next_train_post, next_author, next_subreddit = get_next_post_update(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), current_train_post=train_post)
    
    ip_obj = TrainIps.objects.get(ip=ip_str)

    # Fetching and pushing the next train post into database asynchronously (while the page is loaded) so process is seamless
    a = get_next_post_update.delay(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'), next_train_post)
    while True:
        try:
            next_post = TrainData.objects.filter(~Q(train_ips=ip_obj),~Q(post_title=train_post), times_answered__lt = max_answers)[0]
        except: # If the next train post wasn't pushed to database yet
            
            while a.state != "SUCCESS":
                time.sleep(0.1)
            continue 
        break # Only when next post fetching is done break while loop
    
    
    if request.method == "POST":
        train_post, author, subreddit = next_post.post_title, next_post.author, next_post.subreddit

    try:
        print(request.META['HTTP_REFERER'])
        referral = "here"
    except:
        referral = "other"
                        
    return render(request, "LoveHateGame/train.html", {"post_title": train_post, "author":author, "subreddit":subreddit, "referral":referral})
        
    
