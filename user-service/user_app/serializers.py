from rest_framework import serializers 
from django.contrib.auth import get_user_model 
from user_app.models import UserProfile 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    email = serializers.ReadOnlyField(source="user.email")
    user_created_at = serializers.ReadOnlyField(source="user.date_joined")
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "username",
            "email",
            "phone",
            "gender",
            "dob",
            "country",
            "state",
            "city",
            "pincode",
            "full_address",
            "avatar",
            "avatar_url",
            "user_created_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


    def update(self, instance, validated_data): 
        """ 
        instance = UserProfile 
        instance.user = User 
        """ 
        user = instance.user 
        
        if "username" in validated_data: 
            user.username = validated_data.pop("username") 
            
        if "phone" in validated_data: 
            user.phone = validated_data["phone"] 
            
        user.save() 
        
        return super().update(instance, validated_data)

    def get_avatar_url(self, obj):
        request = self.context.get("request", None)
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        default_path = "/media/avatars/default.png"
        return request.build_absolute_uri(default_path) if request else default_path

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("avatar", None)
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer): 
    @classmethod 
    def get_token(cls, user): 
        token = super().get_token(user)

        token["id"] = str(user.id) 
        token["email"] = user.email 
        token["username"] = user.username 
        token["role"] = user.role 
        token["phone"] = user.phone 
        token["vendor_approved"] = user.vendor_approved

        return token