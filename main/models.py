from django.db import models
from django.contrib.auth.models import User


class SearchQ(models.Model):
    query = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logged_user', null=True)
    score = models.FloatField(null=True)
    date = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.query

class TrainIps(models.Model):
    ip = models.GenericIPAddressField(null=True)



class TrainData(models.Model):
    post_title = models.CharField(max_length=200)
    times_answered = models.IntegerField(null=True, default=0)
    date = models.DateTimeField(null=True)
    positive_score = models.IntegerField(null=True, default=0)
    train_ips = models.ManyToManyField(TrainIps)
    
class ImportantVars(models.Model):
    date = models.DateField()
    purpose = models.CharField(max_length=200, null=True)
