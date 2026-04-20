# owner/forms.py
from django import forms
from .models import Vehicle, StationBooking, ServiceRequest
from accounts.models import User
from django.contrib.auth import get_user_model

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        # We replaced the old battery fields with 'battery_level' and added 'vehicle_type'
        fields = ['make', 'model', 'registration_number', 'battery_level', 'vehicle_type']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'model': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'registration_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'battery_level': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'max': 100, 'min': 0}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
        }
        
        User = get_user_model()

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'registration_number', 'battery_level', 'vehicle_type']

class StationBookingForm(forms.ModelForm):
    class Meta:
        model = StationBooking
        fields = ['vehicle', 'station', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Ensure user can only select THEIR vehicles
            self.fields['vehicle'].queryset = Vehicle.objects.filter(user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        station = cleaned_data.get('station')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        # 1. CHECK WALLET BALANCE (Assuming a minimum base cost of $10 for validation)
        if self.user and hasattr(self.user, 'wallet'):
            if self.user.wallet.balance < 10.00:
                raise forms.ValidationError("Insufficient wallet balance. Please add funds before booking.")

        # 2. DOUBLE BOOKING PREVENTION
        if station and date and start_time and end_time:
            overlapping_bookings = StationBooking.objects.filter(
                station=station,
                date=date,
                status__in=['pending', 'approved']
            ).filter(
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if self.instance.pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)

            if overlapping_bookings.exists():
                raise forms.ValidationError("This time slot is already booked. Please select another time.")
        return cleaned_data

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['vehicle', 'service_center', 'issue_description']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        # ADDED: 'phone_number' (Change to 'phone' if that is your model's field name)
        fields = ['first_name', 'last_name', 'email', 'phone_number']