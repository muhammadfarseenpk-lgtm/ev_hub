# admin_module/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User

class AdminRoleCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
            'role': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:ring-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforce rule: Admin can only create these specific roles
        self.fields['role'].choices = [
            (User.RoleChoices.STATION_OPERATOR, 'Charging Station Operator'),
            (User.RoleChoices.SERVICE_CENTER, 'Service Center')
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_approved = True  # Auto-approve accounts created by Admin
        if commit:
            user.save()
        return user