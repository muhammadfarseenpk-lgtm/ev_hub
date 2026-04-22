from django.db import models
from django.conf import settings

class ChargingStation(models.Model):
    # Linked directly to the Operator user
    operator = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='operated_station', null=True, blank=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    
    # New Operator Fields
    operating_hours = models.CharField(max_length=100, default="24/7")
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE')
    base_rate = models.DecimalField(max_digits=6, decimal_places=2, default=10.00, help_text="Base rate per booking/hour")
    # Add this right under base_rate in ChargingStation
    is_dynamic_pricing = models.BooleanField(default=False, help_text="Enable automatic surge pricing during peak hours")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StationReview(models.Model):
    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} Stars for {self.station.name}"

class Charger(models.Model):
    TYPE_CHOICES = (
        ('slow', 'Slow (AC)'),
        ('fast', 'Fast (DC)'),
    )
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('offline', 'Offline'),
        ('faulty', 'Faulty'),
    )
    
    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE, related_name='chargers')
    charger_id = models.CharField(max_length=50, help_text="e.g., CHG-01")
    charger_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='fast')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.station.name} - {self.charger_id}"

class RevenueRecord(models.Model):
    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE, related_name='revenue_records')
    booking_id = models.IntegerField(help_text="Reference to the StationBooking ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} for {self.station.name} on {self.date.strftime('%Y-%m-%d')}"