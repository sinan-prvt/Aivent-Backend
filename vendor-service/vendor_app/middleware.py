import os
import jwt
from types import SimpleNamespace
from django.conf import settings

JWT_SIGNING_KEY = os.getenv("JWT_SIGNING_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class JWTBridgeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")

        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

            try:
                key = JWT_SIGNING_KEY or settings.SECRET_KEY
                decoded = jwt.decode(
                    token,
                    key=key,
                    algorithms=[JWT_ALGORITHM],
                    options={"verify_exp": True}
                )

                uid = decoded.get("id") or decoded.get("user_id") or decoded.get("sub")
                role = decoded.get("role")

                request.user = SimpleNamespace(
                    id=uid,
                    role=role,
                    is_authenticated=True
                )
                request.jwt_payload = decoded

            except Exception:
                pass

        return self.get_response(request)
