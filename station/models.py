# station/models.py
from django.db import models
from django.conf import settings

class ChargingStation(models.Model):
    operator = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='station_profile')
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

class Charger(models.Model):
    class StatusChoices(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        IN_USE = 'IN_USE', 'In Use'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'
        FAULTED = 'FAULTED', 'Faulted'

    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE, related_name='chargers')
    charger_id_string = models.CharField(max_length=50, unique=True)
    power_kw = models.DecimalField(max_digits=6, decimal_places=2)
    connector_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.AVAILABLE)
    dynamic_price_per_kwh = models.DecimalField(max_digits=5, decimal_places=2)