from django.contrib import admin

from .models import Classifier, SearchQ, Sentence, TrainIps
from .models import TrainData
from .models import ImportantVars

admin.site.register(SearchQ)
admin.site.register(TrainData)
admin.site.register(ImportantVars)
admin.site.register(TrainIps)
admin.site.register(Sentence)
admin.site.register(Classifier)

# Register your models here.
