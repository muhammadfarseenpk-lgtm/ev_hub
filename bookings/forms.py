# bookings/forms.py
from django import forms
from .models import Booking
from django.utils import timezone
from django.core.exceptions import ValidationError

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time < timezone.now():
                raise ValidationError("Start time cannot be in the past.")
            if end_time <= start_time:
                raise ValidationError("End time must be strictly after the start time.")
        return cleaned_data