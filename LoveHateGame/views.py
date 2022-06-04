from django.shortcuts import render
from main.emotion_check import get_random_post
from main.models import TrainData, TrainIps
from django.db.models import Q
import datetime
# Create your views here.

global train_post
train_post = None

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def train(request):
    global train_post
    max_answers = 3
    ip_str = get_client_ip(request)
    if request.method == "POST":
        # if "positive" in requ est.POST:
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

    try:
        if 'ip_obj' not in locals():
            ip_obj = TrainIps.objects.get(ip=ip_str)
        # print(TrainData.train_ips.through.objects.all())
        post = TrainData.objects.filter(~Q(train_ips=ip_obj), times_answered__lt = max_answers)[0]
    except:
        train_post = get_random_post()
        new_post = TrainData(post_title=train_post, date=datetime.datetime.now())
        new_post.save()
    else:
        train_post = post.post_title
        
    return render(request, "LoveHateGame/train.html", {"post_title": train_post})
        
    
