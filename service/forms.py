from django import forms
from django.contrib.auth import get_user_model
from .models import ServiceCenter, ServiceAppointment, InventoryItem, PartOrder

User = get_user_model()

class ServiceCenterForm(forms.ModelForm):
    class Meta:
        model = ServiceCenter
        fields = ['name', 'contact_details', 'service_capabilities']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'contact_details': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'service_capabilities': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition', 'rows': 3, 'placeholder': 'e.g., Battery diagnostics, Motor repair, Tire alignment'}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['part_name', 'quantity', 'threshold', 'price']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'threshold': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition', 'step': '0.01'}),
        }
        
class PartOrderForm(forms.ModelForm):
    class Meta:
        model = PartOrder
        fields = ['quantity', 'status']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
        }

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceAppointment
        fields = ['vehicle', 'date', 'time', 'issue_description']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition'}),
            'issue_description': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:border-[#8b5cf6] focus:ring-1 focus:ring-[#8b5cf6] outline-none transition', 'rows': 3, 'placeholder': 'Describe the issue...'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the vehicle dropdown to ONLY the cars owned by this EV Owner
        self.fields['vehicle'].queryset = user.vehicles.all()