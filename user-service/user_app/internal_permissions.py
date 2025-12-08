import os
from rest_framework.permissions import BasePermission

INTERNAL_TOKEN = os.getenv("USER_SERVICE_INTERNAL_TOKEN") or os.getenv("INTERNAL_TOKEN")

class InternalServicePermission(BasePermission):
    def has_permission(self, request, view):
        auth = request.META.get("HTTP_AUTHORIZATION") or request.headers.get("Authorization") or ""
        if not auth or not auth.startswith("Bearer "):
            return False
        token = auth.split(" ", 1)[1].strip()
        return token == INTERNAL_TOKEN