# Create your tasks here
from celery import shared_task
from celery import Celery

app = Celery('tasks', broker='rediss://:pba041f448e29eb5ae3008eb717539810314741333e3b7fac3b68f225554b377d@ec2-52-50-219-146.eu-west-1.compute.amazonaws.com:7740')

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)