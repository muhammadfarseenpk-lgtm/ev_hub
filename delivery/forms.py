# delivery/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import DeliveryPartnerProfile

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500'})


class DeliveryProfileForm(forms.ModelForm):
    class Meta:
        model = DeliveryPartnerProfile
        # We explicitly use license_plate and vehicle_type here instead of vehicle_number
        fields = ['assigned_service_center', 'vehicle_type', 'license_plate', 'is_available']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500'})