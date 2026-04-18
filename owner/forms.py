# owner/forms.py
from django import forms
from .models import Vehicle
from accounts.models import User

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'registration_number', 'battery_capacity_kwh', 'current_battery_level']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'model': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'registration_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'battery_capacity_kwh': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'current_battery_level': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'max': 100, 'min': 0}),
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