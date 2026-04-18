# station/forms.py
from django import forms
from .models import ChargingStation, Charger
from accounts.models import User

class StationProfileForm(forms.ModelForm):
    class Meta:
        model = ChargingStation
        fields = ['name', 'latitude', 'longitude', 'contact_number', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'step': '0.000001'}),
            'contact_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }

class ChargerForm(forms.ModelForm):
    class Meta:
        model = Charger
        fields = ['charger_id_string', 'power_kw', 'connector_type', 'status', 'dynamic_price_per_kwh']
        widgets = {
            'charger_id_string': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'placeholder': 'e.g. CHG-001'}),
            'power_kw': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'step': '0.1'}),
            'connector_type': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'placeholder': 'e.g. CCS2, CHAdeMO'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'dynamic_price_per_kwh': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'step': '0.01'}),
        }

class OperatorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
        }