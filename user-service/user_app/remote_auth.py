# user_app/remote_auth.py (update the user creation part)
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
import logging
import uuid

logger = logging.getLogger(__name__)
User = get_user_model()

class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION") or request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1].strip()
        try:
            backend = TokenBackend(algorithm="RS256", verifying_key=settings.AUTH_PUBLIC_KEY)
            payload = backend.decode(token, verify=True)
        except Exception as exc:
            logger.debug("Token decode error: %s", exc)
            raise AuthenticationFailed("Invalid token")

        remote_id = payload.get("user_id") or payload.get("id") or payload.get("sub")
        email = payload.get("email")

        if not remote_id and not email:
            raise AuthenticationFailed("Token missing user identifier")

        # Try to find an existing user
        user = None
        if remote_id:
            user = User.objects.filter(id=remote_id).first()
        if not user and email:
            user = User.objects.filter(email=email).first()

        if not user:
            # create a local user safely
            base_username = (email.split("@")[0] if email else f"user_{remote_id or 'anon'}")
            username = base_username
            # Ensure username uniqueness with retries
            for attempt in range(3):
                try:
                    with transaction.atomic():
                        user, created = User.objects.get_or_create(
                            username=username,
                            defaults={
                                "email": email or f"user-{remote_id}@example.invalid",
                                "is_active": True,
                            }
                        )
                    break
                except IntegrityError as e:
                    logger.warning("Username collision when creating user: %s (attempt %d)", username, attempt)
                    # append short uuid suffix and retry
                    username = f"{base_username}_{uuid.uuid4().hex[:6]}"
            else:
                # last resort: force create with uuid username
                username = f"{base_username}_{uuid.uuid4().hex}"
                user = User.objects.create_user(
                    username=username,
                    email=email or f"user-{remote_id}@example.invalid",
                    is_active=True
                )

        # optional sync role
        role = payload.get("role")
        if role and getattr(user, "role", None) != role:
            user.role = role
            user.save(update_fields=["role"])

        return (user, None)
