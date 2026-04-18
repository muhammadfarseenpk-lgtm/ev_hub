from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

# 1. Public Registration (Only EV Owners)
class EVOwnerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.RoleChoices.EV_OWNER # Hardcoded security rule
        if commit:
            user.save()
        return user

# 2. Admin Creation Form (For Operators & Service Centers)
class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Admin can only create these two roles
        self.fields['role'].choices = [
            (User.RoleChoices.STATION_OPERATOR, 'Charging Station Operator'),
            (User.RoleChoices.SERVICE_CENTER, 'Service Center')
        ]

# 3. Service Center Creation Form (For Delivery Partners)
class DeliveryPartnerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.RoleChoices.DELIVERY_PARTNER # Hardcoded security rule
        user.is_approved = True # Approved by the Service Center creating them
        if commit:
            user.save()
        return user