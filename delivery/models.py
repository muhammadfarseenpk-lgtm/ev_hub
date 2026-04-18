# delivery/models.py
from django.db import models
from django.conf import settings
from service.models import ServiceCenter

class DeliveryPartnerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_profile')
    assigned_service_center = models.ForeignKey(ServiceCenter, on_delete=models.SET_NULL, null=True)
    vehicle_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

class DeliveryOrder(models.Model):
    class StatusChoices(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'

    partner = models.ForeignKey(DeliveryPartnerProfile, on_delete=models.CASCADE, related_name='deliveries')
    destination_address = models.TextField()
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)