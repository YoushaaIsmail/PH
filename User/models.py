from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django_resized import ResizedImageField

import os
def upload_to(inst,filename):
      base_path="profile"
      safe_filename=str(filename)
      final_path=os.path.join(base_path,safe_filename)
      return final_path

class User(AbstractUser):
      photo=ResizedImageField(upload_to=upload_to,null=True,blank=True)
      birthy_day=models.DateField(null=True)
      is_verified = models.BooleanField(default=False)
      otp= models.CharField(max_length=6,null=True,blank=True)
