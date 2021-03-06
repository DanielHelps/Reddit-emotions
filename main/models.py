from django.db import models
from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField


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
    post_title = models.CharField(max_length=200, unique=True)
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
    value = models.IntegerField(null=True)
    
    def __str__(self):
        return self.purpose
    
class Classifier(models.Model):
    classifier_obj = PickledObjectField(null=True)
    classifier_date = models.DateField()
     
    def __str__(self):
        return f'{self.classifier_date} classifier'
    
class top_100(models.Model):
    top_obj = PickledObjectField(null=True)
    pos_date = models.DateField(null=True)
    neg_date = models.DateField(null=True)
    
    def __str__(self):
        if self.neg_date == None:
            return f'{self.pos_date} positive top 100'
        else:
            return f'{self.neg_date} negative top 100'
    