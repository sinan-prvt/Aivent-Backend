from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.response import Response 
from user_app.models import UserProfile
from .internal_permissions import InternalServicePermission

User = get_user_model()


class InternalUserCreateView(APIView):
    permission_classes = [InternalServicePermission]

    def post(self, request):
        data = request.data
        remote_id = str(data.get("id")) 
        email = data.get("email")

        if not remote_id: 
            return Response({"detail": "Missing id"}, status=400)

        user = User.objects.filter(remote_id=remote_id).first()

        if not user and email: 
            user = User.objects.filter(email=email).first()

        if not user: 
            raw_username = data.get("username") 
            if raw_username: 
                username = raw_username 
            elif email: 
                username = email.split("@")[0] 
            else: username = f"user_{remote_id}"
            
            final_email = email if email else f"user_{remote_id}@noemail.local" 
            
            user = User.objects.create( 
                remote_id=remote_id, 
                email=final_email, 
                username=username, 
                is_active=True, 
            )

        changed = False 
        for field in ( 
            "username", "email", "full_name", "phone", "role", 
            "email_verified", "vendor_approved", "is_active" ): 
            
            if field in data and getattr(user, field) != data[field]: 
                setattr(user, field, data[field]) 
                    
                changed = True

        if changed: 
            user.save()
            
        return Response({"id": user.id}, status=200)


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



