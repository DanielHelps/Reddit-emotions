# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search requests', views.search_requests, name='search_requests'),
    path('search=<str:query>/', views.emotion_check_view, name='emotion check'),
]