from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from datetime import datetime, timedelta
from django.conf import settings
import jwt

friend_status_choices = [
    ("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected"),
]

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, **data):
        """
        Create and save a User with the given email and password.
        """
        email = data.pop("email")
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        password = data.pop("password")
        data["fullname"] = f'{data.get("first_name") or  ""} {data.get("last_name") or  ""}'
        user = self.model(email=email, **data)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(**extra_fields)

class User(AbstractUser):
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    username = None
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_access_token(self):
        # Generate JWT token
        exp = datetime.now() + timedelta(seconds=settings.JWT_EXPIRATION_TIME)
        token_payload = {
            'user_id': self.id,
            'exp': exp
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')
        return token, exp
    
    def clean(self):
        super().clean()
        self.fullname = self.get_full_name()

class UserFriendMapper(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "user") #delete this record when user is deleted
    friend = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "friend") #delete this record when friend is deleted
    status = models.CharField(max_length=20, choices = friend_status_choices, default = "pending",)
    created_at = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = ('user', 'friend')