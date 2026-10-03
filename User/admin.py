from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# admin.site.register(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets=(
        (None,{
        'classes':('wide',),
        'fields':('username','password1','password2','photo','birthy_day','is_verified','otp'),
        }),
    )