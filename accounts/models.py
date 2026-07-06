from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan_tier = models.CharField(max_length=20, default='FREE') # FREE, PREMIUM, ENTERPRISE
    storage_used = models.BigIntegerField(default=0) # Track in bytes
    storage_limit = models.BigIntegerField(default=524288000) # 500MB default for free tier
    api_key = models.CharField(max_length=64, blank=True, null=True, unique=True)
    google_linked = models.BooleanField(default=False)
    github_linked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_api_key(self):
        self.api_key = uuid.uuid4().hex + uuid.uuid4().hex
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Profile - {self.plan_tier}"

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
