from rest_framework import serializers

from user_app.models import UserProfile




class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    avatar = serializers.ImageField(required=False, write_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "username",
            "full_name",
            "phone",
            "gender",
            "dob",
            "avatar",
            "avatar_url",
            "country",
            "state",
            "city",
            "pincode",
            "full_address",
        ]

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



# class EnableMfaSerializer(serializers.Serializer):
#     pass


# class ConfirmEnableMfaSerializer(serializers.Serializer):
#     secret = serializers.CharField()
#     code = serializers.CharField()


# class VerifyMFASerializer(serializers.Serializer):
#     session_id = serializers.UUIDField()
#     code = serializers.CharField()

