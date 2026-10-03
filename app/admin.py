from django.contrib import admin
from django.apps import apps
from django.db import models
from .models import *
app_models = apps.get_app_config('app').get_models()  # بدل 'app' باسم تطبيقك

for model in app_models:

    admin.site.register(model)
