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

        token = auth.split(" ")[1]

        try:
            backend = TokenBackend(
                algorithm="HS256",
                signing_key=settings.JWT_SIGNING_KEY,
            )
            payload = backend.decode(token, verify=True)

        except Exception as e:
            raise AuthenticationFailed("Invalid or expired token")

        user = SimpleNamespace(
            id=payload.get("user_id"),
            email=payload.get("email"),
            role=payload.get("role"),
        )
        return (user, None)