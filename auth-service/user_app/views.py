from rest_framework import generics
from rest_framework.response import Response 
from django.contrib.auth import get_user_model 
from .serializers import ( UserProfileSerializer, ) 
from rest_framework.views import APIView 
from .permissions import IsVendor, IsAdmin, IsCustomer 
from rest_framework import permissions 
from rest_framework.parsers import MultiPartParser, FormParser 
from user_app.models import UserProfile 
from rest_framework_simplejwt.views import TokenObtainPairView 
from .serializers import CustomTokenObtainPairSerializer 
from rest_framework_simplejwt.authentication import JWTAuthentication


User = get_user_model()




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
    
