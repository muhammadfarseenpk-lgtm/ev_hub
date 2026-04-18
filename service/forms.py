# service/forms.py
from django import forms
from .models import ServiceCenter, Inventory

class ServiceCenterProfileForm(forms.ModelForm):
    class Meta:
        model = ServiceCenter
        fields = ['name', 'address', 'contact_email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500', 'rows': 3}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['part_name', 'stock_quantity', 'reorder_threshold']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'reorder_threshold': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
        }
        
        # Add this to service/forms.py
from .models import Appointment

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['vehicle', 'scheduled_time', 'issue_description']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border rounded-md'}),
            'issue_description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md', 'rows': 3}),
            'vehicle': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the vehicle dropdown to ONLY the cars owned by this user
        self.fields['vehicle'].queryset = user.vehicles.all()
        
        # service/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class DeliveryPartnerCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-2 border rounded'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500'})