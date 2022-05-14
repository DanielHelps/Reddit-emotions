from django.db import models
from django.contrib.auth.models import User


class SearchQ(models.Model):
    query = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logged_user', null=True)
    score = models.FloatField(null=True)
    date = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.query

    
        
