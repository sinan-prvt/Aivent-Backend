from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from user_app.internal_views import (
    InternalUserCreateView,
    InternalApproveVendorView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("user_app.urls")),

    path("api/internal/users/", InternalUserCreateView.as_view()),
    path("api/internal/users/<uuid:user_id>/approve-vendor/", InternalApproveVendorView.as_view()),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
