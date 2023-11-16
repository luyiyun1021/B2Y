from django.contrib import admin
from bili2youtube.models import UserIDMapping, VideoIDMapping

# Register your models here.
admin.site.register(UserIDMapping)
admin.site.register(VideoIDMapping)
