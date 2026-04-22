from django.db import models
from django.conf import settings

class ServiceCenter(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_center')
    name = models.CharField(max_length=255)
    contact_details = models.CharField(max_length=255)
    service_capabilities = models.TextField(help_text="e.g., Battery diagnostics, Motor repair")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceAppointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE, related_name='appointments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_appointments')
    
    # We reference the Vehicle model from your owner app
    vehicle = models.ForeignKey('owner.Vehicle', on_delete=models.CASCADE, related_name='service_appointments')
    
    # Repair Tracking Fields
    issue_description = models.TextField()
    technician = models.CharField(max_length=100, blank=True, null=True, help_text="Assigned mechanic")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    date = models.DateField()
    time = models.TimeField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle} at {self.center.name}"

class InventoryItem(models.Model):
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE, related_name='inventory')
    part_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    threshold = models.IntegerField(default=5, help_text="Alert if stock falls below this")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.part_name} ({self.quantity} left)"

class PartOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('delivered', 'Delivered'),
    )
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class WarrantyClaim(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    appointment = models.OneToOneField(ServiceAppointment, on_delete=models.CASCADE, related_name='warranty')
    part_name = models.CharField(max_length=100, default='Unknown Part')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ServiceRevenue(models.Model):
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE, related_name='revenue_records')
    appointment = models.OneToOneField(ServiceAppointment, on_delete=models.CASCADE, related_name='revenue')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)