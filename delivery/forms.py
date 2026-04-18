# delivery/forms.py
from django import forms
from .models import DeliveryPartnerProfile
from accounts.models import User

class DeliveryProfileForm(forms.ModelForm):
    class Meta:
        model = DeliveryPartnerProfile
        fields = ['vehicle_number', 'is_available']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'placeholder': 'e.g. MH-12-AB-1234'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
        }