from django.db import models
from django.contrib.auth.models import User


class Sentence(models.Model):
    sentence = models.CharField(max_length=1000, null=True)
    sentence_score = models.FloatField(null=True)
    
class SearchQ(models.Model):
    query = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logged_user', null=True)
    score = models.FloatField(null=True)
    date = models.DateTimeField(null=True)
    most_positive = models.ManyToManyField(Sentence, related_name='most_positive')
    most_negative = models.ManyToManyField(Sentence, related_name='most_negative')

    
    def __str__(self):
        return self.query

class TrainIps(models.Model):
    ip = models.GenericIPAddressField(null=True)
    
    def __str__(self):
        return self.ip


class TrainData(models.Model):
    post_title = models.CharField(max_length=200)
    author = models.CharField(null=True, max_length=200)
    subreddit = models.CharField(null=True, max_length=200)
    times_answered = models.IntegerField(null=True, default=0)
    date = models.DateTimeField(null=True)
    positive_score = models.IntegerField(null=True, default=0)
    train_ips = models.ManyToManyField(TrainIps)
    
    def __str__(self):
        return self.post_title
    
    
    
class ImportantVars(models.Model):
    date = models.DateField()
    purpose = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return self.purpose
    
