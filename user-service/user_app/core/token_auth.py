from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from types import SimpleNamespace
from django.conf import settings


class RemoteJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1]

        try:
            backend = TokenBackend(
                algorithm="HS256",
                signing_key=settings.AUTH_JWT_SIGNING_KEY
            )
            payload = backend.decode(token, verify=True)
        except Exception:
            raise AuthenticationFailed("Invalid token")

        user = SimpleNamespace(
            id=payload.get("user_id") or payload.get("id"),
            email=payload.get("email"),
            role=payload.get("role"),
            is_authenticated=True
        )

        return (user, None)
