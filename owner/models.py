from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet: ${self.balance}"

class Vehicle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    battery_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=100)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"

class StationBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_station_bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    
    # Notice how these are on two separate lines now:
    station = models.ForeignKey('station.ChargingStation', on_delete=models.CASCADE, related_name='bookings')
    charger = models.ForeignKey('station.Charger', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # ... inside StationBooking
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, default=10.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

# ---> ADD A BLANK LINE HERE <---

class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
# ... rest of your code
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    service_center = models.ForeignKey('service.ServiceCenter', on_delete=models.CASCADE) 
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class EmergencySOS(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sos_alerts')
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('resolved', 'Resolved')], default='active')
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# --- SIGNALS ---
@receiver(pre_save, sender=StationBooking)
def deduct_wallet_on_approval(sender, instance, **kwargs):
    if instance.pk: 
        old_instance = StationBooking.objects.get(pk=instance.pk)
        
        if old_instance.status != 'approved' and instance.status == 'approved':
            wallet = instance.user.wallet
            
            if wallet.balance >= instance.estimated_cost:
                wallet.balance -= instance.estimated_cost
                wallet.save()
                
                Notification.objects.create(
                    user=instance.user,
                    title="Payment Deducted",
                    message=f"${instance.estimated_cost} was deducted for your approved booking at {instance.station.name}."
                )
            else:
                instance.status = 'rejected'