# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search=<str:query>/', views.emotion_check_view, name='emotion check'),
]