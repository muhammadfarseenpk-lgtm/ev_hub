# service/models.py
from django.db import models
from django.conf import settings
from owner.models import Vehicle

class ServiceCenter(models.Model):
    manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_center_profile')
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_email = models.EmailField()

class Appointment(models.Model):
    class StatusChoices(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    service_center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.SCHEDULED)

class Inventory(models.Model):
    service_center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=200)
    stock_quantity = models.PositiveIntegerField()
    reorder_threshold = models.PositiveIntegerField()
    
    # Add this to the bottom of service/models.py
class WarrantyClaim(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Validation'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    # Assuming you have imported Vehicle from owner app
    vehicle = models.ForeignKey('owner.Vehicle', on_delete=models.CASCADE, related_name='warranty_claims')
    service_center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=100)
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Warranty: {self.part_name} - {self.vehicle.registration_number}"