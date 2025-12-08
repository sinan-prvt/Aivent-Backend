from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .internal_permissions import InternalServicePermission

User = get_user_model()


class InternalUserCreateView(APIView):
    permission_classes = [InternalServicePermission]

    def post(self, request):
        data = request.data

        email = data.get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                username=email.split("@")[0],
                role=data.get("role", "vendor"),
                email_verified=data.get("email_verified", True),
                is_active=data.get("is_active", False),
                vendor_approved=data.get("vendor_approved", False),
            )
        user = User.objects.filter(email=email).first()
        if user:
            return Response({"id": str(user.id)}, status=status.HTTP_200_OK)

        user = User.objects.create(
            email=email,
            username=email.split("@")[0],
            role=data.get("role", "vendor"),
            email_verified=data.get("email_verified", True),
            is_active=data.get("is_active", False),
            vendor_approved=data.get("vendor_approved", False),
        )

        return Response({"id": str(user.id)}, status=status.HTTP_201_CREATED)



class InternalApproveVendorView(APIView):
    permission_classes = [InternalServicePermission]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        user.vendor_approved = True
        user.is_active = True
        user.role = "vendor"
        user.save()

        return Response({"detail": "Vendor approved"}, status=status.HTTP_200_OK)



