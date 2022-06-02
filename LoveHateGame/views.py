from django.shortcuts import render
from main.emotion_check import get_random_post
from main.models import TrainData
from django.db.models import Q
# Create your views here.

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def train(request):
    max_answers = 3
    ip = get_client_ip(request)
    if request.method == "POST":
        if "positive" in request.POST:
            print("positive")
            pass
        elif "negative" in request.POST:
            print("negative")
            pass
        else:
            print("none")
            pass
    try:
        post = TrainData.objects.get(~Q(ip=ip), times_answered__lt = max_answers)
    except:
        post_title = get_random_post()
    else:
        post_title = post.post_title
        
    return render(request, "LoveHateGame/train.html", {"post_title": post_title})
        
    
