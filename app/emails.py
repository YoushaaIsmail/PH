# emails.py
from django.core.mail import send_mail
import random
from django.conf import settings
from User.models import User
from django.utils import timezone
from datetime import datetime

def send_otp_via_email(email1):
    subject = "Your Password Reset OTP"
    otp1 = random.randint(100000, 999999)  # 6-digit OTP
    message = f'Your OTP for password reset is: {otp1}\n\nThis OTP is valid for 10 minutes.\n\nIf you did not request this, please ignore this email.'
    email_from = settings.EMAIL_HOST_USER
    
    try:
        user_obj = User.objects.get(email=email1)
        user_obj.otp = otp1
        # Store the current timestamp in the session instead of adding a new field
        print(user_obj.otp)
        user_obj.save()
        
        send_mail(subject, message, email_from, [email1])
        return True
    except User.DoesNotExist:
        return False