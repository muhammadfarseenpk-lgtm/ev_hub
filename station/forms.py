from django import forms
from django.contrib.auth import get_user_model
from .models import ChargingStation, Charger

User = get_user_model()

class StationProfileForm(forms.ModelForm):
    class Meta:
        model = ChargingStation
        # These are the correct fields from our upgraded model
        fields = ['name', 'location', 'operating_hours', 'status', 'base_rate', 'is_dynamic_pricing']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'operating_hours': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition', 'placeholder': 'e.g., 24/7 or 8 AM - 10 PM'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'base_rate': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition', 'step': '0.01'}),
            'is_dynamic_pricing': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-[#8b5cf6] rounded focus:ring-[#8b5cf6]'}),
        }

class ChargerForm(forms.ModelForm):
    class Meta:
        model = Charger
        fields = ['charger_id', 'charger_type', 'status']
        widgets = {
            'charger_id': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition', 'placeholder': 'e.g., CHG-01'}),
            'charger_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
        }

class OperatorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
        }