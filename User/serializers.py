from rest_framework import serializers
from .models import User
from dj_rest_auth.serializers import UserDetailsSerializer
from .emails import *
from app.models import Wallet
class Users2(UserDetailsSerializer):
    class Meta:
        model=User
        fields=['birthy_day','photo','email']        

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user1 = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user1.set_password(validated_data['password'])
        user1.save()
        Wallet.objects.create(
            user=user1,
            Amount =0      )
        

        # إرسال OTP
        send_otp_via_email(validated_data['email'])

        return user1
    

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        attrs['user'] = user
        return attrs

# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                # if user.is_active:
                    data['user'] = user
                # else:
                #     raise serializers.ValidationError('Account is disabled')
            else:
                raise serializers.ValidationError('Invalid username or password')
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_verified')


# Alternative version with serializer (recommended)
from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','first_name', 'last_name', 'birthy_day', 'photo', 'is_verified']
        read_only_fields = ['id', 'is_verified']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value