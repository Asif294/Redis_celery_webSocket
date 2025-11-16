import logging
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User, EmailOTP
from account.serializers import (
    UserRegistrationSerializer,
    OTPVerificationSerializer,
    UserLoginSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    UserDetailsSerializer
) 

logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        request_body=UserRegistrationSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description='User created successfully, OTP sent to email'
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Validation error'
            )
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'success': 'Registration successful! Please check your email for OTP verification.',
                'email': user.email,
                'message': 'OTP is valid for 3 minutes. Check spam folder if not found in inbox.'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        request_body=OTPVerificationSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Email verified successfully'
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid or expired OTP'
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='User not found'
            )
        }
    )
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
            
            # Check if already verified
            if user.is_active and user.is_verified:
                return Response({
                    'message': 'Email already verified. You can login now.'
                }, status=status.HTTP_200_OK)
            
            # Get latest unverified OTP
            try:
                email_otp = EmailOTP.objects.filter(
                    user=user, 
                    is_verified=False
                ).latest('created_at')
            except EmailOTP.DoesNotExist:
                return Response({
                    'error': 'No OTP found. Please request a new one.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if OTP expired
            if email_otp.is_expired():
                return Response({
                    'error': 'OTP has expired. Please request a new one.',
                    'expired': True
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify OTP
            if email_otp.otp != otp:
                return Response({
                    'error': 'Invalid OTP. Please check and try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Activate user account
            user.is_active = True
            user.is_verified = True
            user.save()
            
            email_otp.is_verified = True
            email_otp.save()
            
            return Response({
                'success': 'Email verified successfully! You can now login.',
                'username': user.username
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email not found.'
            }, status=status.HTTP_404_NOT_FOUND)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='New OTP sent successfully'
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Email is required'
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='User not found'
            )
        }
    )
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Check if already verified
            if user.is_active and user.is_verified:
                return Response({
                    'message': 'Email already verified. You can login now.'
                }, status=status.HTTP_200_OK)
            
            # Delete old unverified OTPs
            EmailOTP.objects.filter(user=user, is_verified=False).delete()
            
            # Generate new OTP
            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.create(user=user, otp=otp_code)
            
            # Send email
            subject = "Email Verification - New OTP"
            context = {
                'username': user.username,
                'otp': otp_code
            }
            email_body = render_to_string('account/otp_email.html', context)
            
            email_msg = EmailMultiAlternatives(
                subject, 
                '', 
                settings.EMAIL_HOST_USER, 
                [user.email]
            )
            email_msg.attach_alternative(email_body, 'text/html')
            email_msg.send()
            
            return Response({
                'success': 'New OTP sent successfully to your email.',
                'message': 'OTP is valid for 3 minutes.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email not found.'
            }, status=status.HTTP_404_NOT_FOUND)



class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        request_body=UserLoginSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(description='Login successful'),
            status.HTTP_404_NOT_FOUND: openapi.Response(description='Account not found')
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                "access": access_token,  # Frontend should store this in memory
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "profile_picture": user.profile_picture
                }
            }, status=status.HTTP_200_OK)

            # Store refresh token in HttpOnly cookie
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,  # Prevents JavaScript access (XSS protection)
                secure=True,  # Send only over HTTPS in production
                samesite="Lax",  # Helps prevent CSRF issues
            )

            return response
        
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class CookieTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        tags=['Token'],
        responses={
            status.HTTP_401_UNAUTHORIZED: "You are not authorized!",
            status.HTTP_200_OK: "Token refreshed",
        }
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"error": "No refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Inject the refresh token from the cookie into the request data.
        request.data["refresh"] = refresh_token
        
        # Call the parent view to get the new tokens.
        response = super().post(request, *args, **kwargs)
        
        # If a new refresh token is issued, update the HttpOnly cookie.
        if "refresh" in response.data:
            new_refresh = response.data.pop("refresh")  # Removed from response data.
            response.set_cookie(
                key="refresh_token",
                value=new_refresh,
                httponly=True,     # Ensures the cookie is not accessible via JavaScript.
                secure=True,       # Use HTTPS in production.
                samesite="Lax",    # Helps protect against CSRF.
            )
        
        return response


class LogoutView(APIView):
    @swagger_auto_schema(
        tags=['Account'],
        responses={
            status.HTTP_200_OK: "Logout Successful",
            status.HTTP_401_UNAUTHORIZED: "Authentication crediential not provided",
        }
    )
    def post(self, request):
        response = Response({"success": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")  # clear the refresh token cookie
        return response


class AccountDeleteView(APIView):
    @swagger_auto_schema(
        tags=['Account'],
        responses={
            status.HTTP_200_OK: "Account deleted successfully",
            status.HTTP_400_BAD_REQUEST: "An error occurred"
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.is_deleted = True
        user.save(update_fields=["is_active", "is_deleted"])
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            status.HTTP_200_OK: "Password changed successfully",
            status.HTTP_400_BAD_REQUEST: "Validation errors"
        },
        tags=['Account']
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditProfileView(APIView):
    http_method_names = ['put']
    @swagger_auto_schema(
        tags=['Account'],
        request_body=UserProfileUpdateSerializer,
        responses={
            status.HTTP_200_OK: "Profile updated successfully",
            status.HTTP_400_BAD_REQUEST: "Validation errors"
        },
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Profile updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyDetailsAPIView(APIView):
    serializer_class = UserDetailsSerializer

    @swagger_auto_schema(
        tags=['Profile'],
        responses={
            status.HTTP_200_OK: UserDetailsSerializer,
            status.HTTP_401_UNAUTHORIZED: "Authentication credentials were not provided."
        }
    )
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class UserDetailsAPIView(APIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Profile'],
        responses={
            status.HTTP_200_OK: UserDetailsSerializer(),
            status.HTTP_404_NOT_FOUND: "User not found.",
            status.HTTP_400_BAD_REQUEST: "This profile is private."
        }
    )
    def get(self, request, username, *args, **kwargs):
        """
        Get user details by username.
        """
        user = get_object_or_404(User, username=username, is_active=True, is_deleted=False)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)