from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from auth_app.utils import verify_otp
from auth_app.tasks import publish_event_task

User = get_user_model()

class VendorVerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")

        if not user_id or not otp:
            return Response({"detail": "user_id and otp required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)

        if not verify_otp(user, otp, purpose="vendor_register"):
            return Response({"detail": "Invalid OTP"}, status=400)

        user.email_verified = True
        user.save()

        # publish event for vendor-service
        publish_event_task.delay(
            "vendor.created",
            {
                "event": "USER_VENDOR_CREATED",
                "user_id": str(user.id),
                "email": user.email,
                "phone": user.phone,
            }
        )

        return Response({
            "message": "Vendor registered. Waiting for admin approval."
        })
