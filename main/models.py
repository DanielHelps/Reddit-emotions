from django.db import models
from django.contrib.auth.models import User


class SearchQ(models.Model):
    query = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logged_user', null=True)
    score = models.FloatField(null=True)
    date = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.query

class TrainData(models.Model):
    query = models.CharField(max_length=200)
    question = models.CharField(max_length=1000)
    date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_user', null=True)
    is_positive = models.BooleanField()
    
class ImportantVars(models.Model):
    date = models.DateField()
    purpose = models.CharField(max_length=200, null=True)
