# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        EV_OWNER = 'EV_OWNER', 'EV Owner'
        STATION_OPERATOR = 'STATION_OPERATOR', 'Charging Station Operator'
        SERVICE_CENTER = 'SERVICE_CENTER', 'Service Center'
        DELIVERY_PARTNER = 'DELIVERY_PARTNER', 'Delivery Partner'

    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.EV_OWNER)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False) # For optional email verification
    
    def save(self, *args, **kwargs):
        # Admins and EV Owners are auto-approved. Others require manual intervention if needed.
        if self.role in [self.RoleChoices.EV_OWNER, self.RoleChoices.ADMIN] and not self.pk:
            self.is_approved = True
            
        # Ensure Superusers are always ADMIN
        if self.is_superuser:
            self.role = self.RoleChoices.ADMIN
            self.is_approved = True
            self.email_verified = True
            
        super().save(*args, **kwargs)