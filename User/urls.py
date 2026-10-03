from django.urls import path,include
from dj_rest_auth.views import UserDetailsView
from dj_rest_auth.views import UserDetailsView
from .serializers import Users2
from .views import *
from dj_rest_auth.views import LoginView
urlpatterns = [
    path('registration/',include('dj_rest_auth.registration.urls')),
    path('profile/', include('allauth.urls')),
        path('profile1/', include('dj_rest_auth.urls')),
    path('Newlogin/',NewloginView.as_view(),name='login'),
    path('NewRegister/',Newregister,name='NewRegister'),
    path('verify-otp/', verify_otp, name='verify-otp'),
        path('api/login/', login_view, name='api-login'),
    # path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('user/', UserDetailsView.as_view(serializer_class=Users2)),
        # or using the serializer version
    path('api/user/edit-profile-serializer/', edit_user_profile_serializer, name='edit_profile_serializer'),]





