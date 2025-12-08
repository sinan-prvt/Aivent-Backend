from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import (
    UserProfileSerializer,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .permissions import IsVendor, IsAdmin, IsCustomer
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()



class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.profile

    def get_serializer_context(self):
        return {"request": self.request}


class VendorDashboardView(APIView):
    permission_classes = [IsVendor]

    def get(self, request):
        return Response({"message": "Vendor dashboard"})
    

class AdminPanelView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "Admin Panel"})
    

class CustomerHistoryView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        return Response({"orders": []})
    

# class VerifyMFAView(generics.GenericAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = VerifyMFASerializer

#     @swagger_auto_schema(
#         operation_description="Verify MFA TOTP and return JWT tokens",
#         tags=["MFA"]
#     )

#     def post(self, request):
#         s = self.get_serializer(data=request.data)
#         s.is_valid(raise_exception=True)
#         session_id = s.validated_data["session_id"]
#         code = s.validated_data["code"]

#         mfs = MFASession.objects.filter(id=session_id, used=False).first()
#         if not mfs or mfs.is_expired():
#             return Response({"detail": "Invalid or expired MFA session"}, status=400)

#         user = mfs.user
#         if not user.totp_secret:
#             return Response({"detail": "User has no TOTP configured"}, status=400)

#         totp = pyotp.TOTP(user.totp_secret)
#         if not totp.verify(code, valid_window=1):
#             return Response({"detail": "Invalid TOTP code"}, status=400)

#         mfs.used = True
#         mfs.save()

#         refresh = RefreshToken.for_user(user)
#         access = str(refresh.access_token)
#         refresh_token = str(refresh)

#         return Response({
#             "access": access,
#             "refresh": refresh_token,
#         }, status=200)


# class EnableMFAView(generics.GenericAPIView):
#     serializer_class = EnableMfaSerializer
#     permission_classes = [permissions.IsAuthenticated, IsVendor]

#     @swagger_auto_schema(
#         operation_description="Generate TOTP QR and secret for enabling MFA",
#         tags=["MFA"]
#     )

#     def get(self, request):
#         user = request.user
#         secret = pyotp.random_base32()
#         totp = pyotp.TOTP(secret)
#         otpauth = totp.provisioning_uri(name=user.email, issuer_name="AIVENT")
#         qr_b64 = qrcode_base64_from_uri(otpauth)
#         return Response({"secret": secret, "otpauth_url": otpauth, "qr": qr_b64})


# class ConfirmEnableMFAView(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated, IsVendor]
#     serializer_class = ConfirmEnableMfaSerializer

#     @swagger_auto_schema(
#         operation_description="Verify TOTP code to enable MFA",
#         tags=["MFA"]
#     )

#     def post(self, request):
#         s = self.get_serializer(data=request.data)
#         s.is_valid(raise_exception=True)

#         secret = s.validated_data["secret"]
#         code = s.validated_data["code"]

#         totp = pyotp.TOTP(secret)
#         if not totp.verify(code, valid_window=1):
#             return Response({"detail": "Invalid TOTP code"}, status=400)

#         user = request.user
#         user.totp_secret = secret
#         user.mfa_enabled = True
#         user.save()

#         return Response({"detail": "MFA enabled"}, status=200)


# class DisableMFAView(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated, IsVendor]
#     serializer_class = drf_serializers.Serializer


#     @swagger_auto_schema(
#         operation_description="Disable MFA for vendor",
#         tags=["MFA"]
#     )

#     def post(self, request):
#         user = request.user
#         user.totp_secret = None
#         user.mfa_enabled = False
#         user.save()
#         return Response({"detail": "MFA disabled"}, status=200)

