from django.contrib import admin

from .models import SearchQ, Sentence, TrainIps
from .models import TrainData
from .models import ImportantVars

admin.site.register(SearchQ)
admin.site.register(TrainData)
admin.site.register(ImportantVars)
admin.site.register(TrainIps)
admin.site.register(Sentence)

# Register your models here.
