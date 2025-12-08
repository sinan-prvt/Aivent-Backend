from rest_framework import generics, status 
from rest_framework.response import Response 
from rest_framework.permissions import AllowAny, IsAuthenticated 
from django.contrib.auth import get_user_model 
from .serializers import ( UserProfileSerializer, ) 
from rest_framework.views import APIView 
from rest_framework_simplejwt.tokens import RefreshToken, TokenError 
from .permissions import IsVendor, IsAdmin, IsCustomer 
from rest_framework import permissions 
from rest_framework.parsers import MultiPartParser, FormParser 
from user_app.models import UserProfile 
from rest_framework_simplejwt.views import TokenObtainPairView 
from .serializers import CustomTokenObtainPairSerializer 
from django.conf import settings 
import requests 
from rest_framework_simplejwt.authentication import JWTAuthentication


User = get_user_model()


def fetch_identity(auth_header): 
    if not auth_header: 
        return False, {"error": "Missing Authorization header"}
    
    url = settings.AUTH_SERVICE_URL.rstrip("/") + "/api/auth/me/"

    headers = { 
        "Authorization": auth_header.strip(), 
        "Content-Type": "application/json" 
    }

    try: 
        resp = requests.get(url, headers=headers, timeout=5) 
        if resp.status_code == 200: 
            return True, resp.json()
        
        return False, {"error": resp.text, "status": resp.status_code}
    
    except Exception as e: 
        return False, {"error": str(e)}




class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_context(self):
        return {"request": self.request}


class CustomTokenObtainPairView(TokenObtainPairView): 
    serializer_class = CustomTokenObtainPairSerializer 
    

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
    
