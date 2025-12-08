from django.urls import path
from .views import VendorApplyView, VerifyVendorOTPView, PendingVendorsView, VendorApproveView

urlpatterns = [
    path("apply/", VendorApplyView.as_view()),
    path("verify-otp/", VerifyVendorOTPView.as_view()),
    path("admin/pending/", PendingVendorsView.as_view()),
    path("admin/<uuid:vendor_id>/approve/", VendorApproveView.as_view()),
]
