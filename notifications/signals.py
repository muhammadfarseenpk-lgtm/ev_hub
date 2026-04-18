# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from service.models import Appointment
from .models import Notification

@receiver(post_save, sender=Booking)
def notify_booking_changes(sender, instance, created, **kwargs):
    if created:
        # Notify Station Operator of new booking
        Notification.objects.create(
            user=instance.charger.station.operator,
            title="New Booking Request",
            message=f"New booking request for Charger {instance.charger.charger_id_string}."
        )
    else:
        # Notify EV Owner of status changes
        Notification.objects.create(
            user=instance.user,
            title="Booking Status Updated",
            message=f"Your booking at {instance.charger.station.name} is now {instance.get_status_display()}."
        )

@receiver(post_save, sender=Appointment)
def notify_repair_changes(sender, instance, created, **kwargs):
    if not created:
        # Notify EV Owner of repair progress
        Notification.objects.create(
            user=instance.vehicle.user,
            title="Repair Status Updated",
            message=f"Your vehicle repair is now {instance.get_status_display()}."
        )