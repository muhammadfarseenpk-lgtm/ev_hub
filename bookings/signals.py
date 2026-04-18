from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from notifications.models import Notification

@receiver(post_save, sender=Booking)
def create_booking_notification(sender, instance, created, **kwargs):
    if created:
        # Notify Station Operator
        Notification.objects.create(
            user=instance.charger.station.operator,
            title="New Booking Request",
            message=f"New booking request for Charger {instance.charger.charger_id_string}."
        )
    else:
        # Notify User of status change
        Notification.objects.create(
            user=instance.user,
            title="Booking Status Updated",
            message=f"Your booking status is now {instance.status}."
        )