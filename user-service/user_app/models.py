from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager



class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)



class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, default="avatars/default.png")

    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile"
    


# class MFASession(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mfa_sessions")
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     used = models.BooleanField(default=False)

#     def is_expired(self):
#         return timezone.now() >= self.expires_at

#     @classmethod
#     def create_for_user(cls, user, valid_seconds=180):
#         expires = timezone.now() + timedelta(seconds=valid_seconds)
#         return cls.objects.create(user=user, expires_at=expires)


