from django.contrib import admin
from .models import GamePersistentData, UserColorSet, UserRanking, News

admin.site.register(GamePersistentData)
admin.site.register(UserColorSet)
admin.site.register(UserRanking)
admin.site.register(News)
