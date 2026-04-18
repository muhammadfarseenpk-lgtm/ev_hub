# delivery/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from service.models import ServiceCenter

class DeliveryPartnerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_profile')
    assigned_service_center = models.ForeignKey(ServiceCenter, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, default="Van")
    license_plate = models.CharField(max_length=50) # This replaces vehicle_number
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.license_plate}"

class DeliveryTask(models.Model):
    class StatusChoices(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned (Pending Pickup)'
        PICKED_UP = 'PICKED_UP', 'Picked Up (In Transit)'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'

    partner = models.ForeignKey(DeliveryPartnerProfile, on_delete=models.CASCADE, related_name='tasks')
    pickup_address = models.TextField()
    dropoff_address = models.TextField()
    package_details = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task #{self.id} - {self.package_details}"