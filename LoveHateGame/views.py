from django.shortcuts import render
from main.emotion_check import get_random_post

# Create your views here.

def train(request):
    post_title = get_random_post()
    return render(request, "LoveHateGame/train.html", {"post_title": post_title})
