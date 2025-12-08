from django.urls import path
from .views import (
    UserProfileView,
    CustomTokenObtainPairView,
)

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
]
