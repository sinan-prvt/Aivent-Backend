import logging 
from django.conf import settings 
from django.contrib.auth import get_user_model 
from rest_framework.authentication import BaseAuthentication 
from rest_framework.exceptions import AuthenticationFailed 
from rest_framework_simplejwt.backends import TokenBackend



logger = logging.getLogger(__name__)
User = get_user_model()


class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1]

        try:
            backend = TokenBackend(algorithm="RS256", verifying_key=settings.AUTH_PUBLIC_KEY)
            payload = backend.decode(token, verify=True)
        except Exception:
            raise AuthenticationFailed("Invalid token")

        remote_id = str(payload.get("user_id") or payload.get("id"))
        if not remote_id:
            raise AuthenticationFailed("Token missing user ID")

        email = (payload.get("email") or "").strip() or None
        username = (payload.get("username") or "").strip()

        if not username: 
            if email: 
                username = email.split("@")[0] 
            else: 
                username = f"user_{remote_id}"

        final_email = email if email else f"user_{remote_id}@noemail.local"


        user = User.objects.filter(remote_id=remote_id).first()
        if not user and email:
            user = User.objects.filter(email=email).first()
        
        if not user: 
            user = User.objects.create( 
                remote_id=remote_id, 
                email=final_email, 
                username=username, 
                is_active=True, 
            )

        token_role = payload.get("role") 
        if token_role and user.role != token_role: 
            user.role = token_role 
            user.save(update_fields=["role"]) 
        
        return (user, None)

       
       