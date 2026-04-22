from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from bookings.models import Booking
from service.models import Appointment
from .models import Notification

# 1. Handle New Bookings (post_save is good for creations)
@receiver(post_save, sender=Booking)
def notify_new_booking(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.charger.station.operator,
            title="New Booking Request",
            message=f"New booking request for Charger {instance.charger.charger_id_string}."
        )

# 2. Handle Booking Status Updates (pre_save prevents spam)
@receiver(pre_save, sender=Booking)
def notify_booking_status_change(sender, instance, **kwargs):
    if instance.pk: # If the booking already exists
        old_booking = Booking.objects.get(pk=instance.pk)
        if old_booking.status != instance.status: # Only notify if status CHANGED
            Notification.objects.create(
                user=instance.user,
                title="Booking Status Updated",
                message=f"Your booking at {instance.charger.station.name} is now {instance.get_status_display()}."
            )

# 3. Handle Repair Status Updates (pre_save prevents spam)
@receiver(pre_save, sender=Appointment)
def notify_repair_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_appointment = Appointment.objects.get(pk=instance.pk)
        if old_appointment.status != instance.status: # Only notify if status CHANGED
            Notification.objects.create(
                user=instance.vehicle.user,
                title="Repair Status Updated",
                message=f"Your vehicle repair is now {instance.get_status_display()}."
            )