from django.contrib import admin
from .models import CustomUser, File

admin.site.register(CustomUser)
admin.site.register(File)