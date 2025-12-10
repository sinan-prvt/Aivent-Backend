from django.urls import path
from .views import (
    VendorApplyView,
    VerifyVendorOTPView,
    PendingVendorsView,
    VendorApproveView,
)

urlpatterns = [
    path("apply/", VendorApplyView.as_view(), name="vendor-apply"),
    path("verify-otp/", VerifyVendorOTPView.as_view(), name="vendor-verify-otp"),

    # Admin routes
    path("admin/vendors/pending/", PendingVendorsView.as_view(), name="pending-vendors"),
    path("admin/vendors/<uuid:vendor_id>/approve/", VendorApproveView.as_view(), name="vendor-approve"),
]
