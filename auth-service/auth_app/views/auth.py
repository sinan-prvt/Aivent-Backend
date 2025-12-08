from django.contrib.auth import get_user_model
from rest_framework import status, permissions, serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..serializers import (
    CustomLoginSerializer,
    RegisterSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from auth_app.core.captcha_utils import (
    requires_captcha,
    increment_failed_attempts,
    reset_failed_attempts,
)
from auth_app.core.recaptcha import verify_recaptcha
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from auth_app.tasks import send_email_task
from ..utils import create_otp_for_user
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.conf import settings
import logging
from auth_app.tasks import sync_user_to_user_service_task

User = get_user_model()

logger = logging.getLogger(__name__)


class MeView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        user = request.user

        payload = { 
            "id": str(getattr(user, "id", "")), 
            "username": getattr(user, "username", "") or "", 
            "email": getattr(user, "email", "") or "", 
            "full_name": getattr(user, "full_name", "") or "", 
            "phone": getattr(user, "phone", "") or None, 
            "role": getattr(user, "role", "customer"), 
            "email_verified": bool(getattr(user, "email_verified", False)), 
            "vendor_approved": bool(getattr(user, "vendor_approved", False)), 
            "is_active": bool(getattr(user, "is_active", False)), 
            "date_joined": (getattr(user, "date_joined", None).isoformat() 
                if getattr(user, "date_joined", None) else None), 
            }
        return Response(payload, status=200)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    @swagger_auto_schema(
        operation_description="Login with email + password + reCAPTCHA + optional MFA",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        ip = request.META.get("REMOTE_ADDR")
        key = f"{email}:{ip}" if email else ip

        # If captcha is required, validate recaptcha token first
        if requires_captcha(key):
            token = request.data.get("recaptcha_token")
            if not token:
                return Response({
                    "success": False,
                    "message": "reCAPTCHA required",
                    "errors": {"recaptcha": ["This action requires reCAPTCHA verification"]}
                }, status=status.HTTP_400_BAD_REQUEST)

            resp = verify_recaptcha(token, remoteip=ip)
            score = resp.get("score") or 0
            if not resp.get("success") or score < float(settings.RECAPTCHA_MIN_SCORE):
                increment_failed_attempts(key)
                return Response({
                    "success": False,
                    "message": "reCAPTCHA validation failed",
                    "errors": {"recaptcha": ["validation failed"], "score": [score]}
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            # increment failed attempts so captcha is triggered next time
            try:
                increment_failed_attempts(key)
            except Exception:
                pass
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # At this point serializer validated and put validated user on serializer if using CustomLoginSerializer
        user = getattr(serializer, "_validated_user", None)
        reset_failed_attempts(key)

        # async sync user to user-service (non-blocking)
        if user:
            try:
                sync_user_to_user_service_task.delay({
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "role": user.role,
                    "email_verified": user.email_verified,
                    "vendor_approved": user.vendor_approved,
                    "is_active": user.is_active,
                })
            except Exception:
                logger.exception("Failed to dispatch sync task")

        tokens_resp = super().post(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Logged in",
            "data": tokens_resp.data
        }, status=tokens_resp.status_code)



class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user with email + password + OTP verification",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        if response.status_code == 201:
            email = request.data.get("email")
            user = User.objects.filter(email=email).first()

            if user: 
                sync_user_to_user_service_task.delay({ 
                    "id": str(user.id), 
                    "email": user.email, 
                    "username": user.username, 
                    "full_name": user.full_name, 
                    "phone": user.phone, 
                    "role": user.role, 
                    "email_verified": user.email_verified, 
                    "vendor_approved": user.vendor_approved, 
                    "is_active": user.is_active, 
                })

                raw_otp, otp_obj = create_otp_for_user(user, "email_verify")
                send_email_task.delay(
                    subject="AIVENT OTP Verification",
                    message=f"Your OTP is: {raw_otp}",
                    recipient_list=[email],
                )

        return response
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout by blacklisting refresh token",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Could not blacklist token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout from all devices by blacklisting all tokens",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        tokens = OutstandingToken.objects.filter(user=request.user)

        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({"detail": "All tokens revoked"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change user password",
        tags=["Authentication"]
    )

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old = serializer.validated_data["old_password"]
        new = serializer.validated_data["new_password"]

        if not user.check_password(old):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new)
        user.save()

        return Response({"detail": "Password changed successfully"}, status=200)
   