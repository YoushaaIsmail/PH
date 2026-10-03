from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.views import LoginView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny

# Create your views here.
from django.contrib.auth import login
class NewloginView(LoginView):
    def get_response(self):
        response = super().get_response()

        if response.status_code == status.HTTP_200_OK:
            user = self.user
            if user.is_verified:
                token = response.data['key']
                return Response({
                    'status': status.HTTP_200_OK,
                    'message': 'Login successful',
                    'data': {
                        'key': token
                    }
                })
            else:
                return Response({
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'message': 'User is not verified',
                    'data': None
                })
        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('username')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Please provide both email and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user:
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# class LogoutAPIView(APIView):

#     def post(self, request):
#         try:
#             # Delete the token to force re-login
#             request.user.auth_token.delete()
#             return Response({
#                 'message': 'Successfully logged out'
#             }, status=status.HTTP_200_OK)
#         except (AttributeError, Token.DoesNotExist):
#             return Response({
#                 'error': 'User not logged in or token not found'
#             }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def Newregister(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        
        return Response({"message": "User created successfully. OTP sent to email."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user.is_verified = True
        user.otp = ""  # مسح OTP بعد التحقق
        user.save()
        return Response({"message": "Account verified successfully!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_user_profile_serializer(request):
    """
    Edit user profile using serializer
    """
    user = request.user
    serializer = UserProfileSerializer(user, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)