from django.urls import path
from account.views import (
    UserLoginView, 
    UserRegistrationView, 
    LogoutView,
    EditProfileView,
    ChangePasswordView,
    AccountDeleteView,
    MyDetailsAPIView,
    UserDetailsAPIView,
    VerifyOTPView,
    ResendOTPView
)

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # OTP Verification
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    # Profile Management
    path('me/', MyDetailsAPIView.as_view(), name='my-details'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete/', AccountDeleteView.as_view(), name='account-delete'),
    
    # User Details (শেষে রাখুন - এটা catch-all pattern)
    path('<str:username>/', UserDetailsAPIView.as_view(), name='user-details'),
]