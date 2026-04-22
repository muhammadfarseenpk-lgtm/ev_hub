# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class EVOwnerRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False, help_text="Optional, for booking notifications.")

    class Meta(UserCreationForm.Meta):
        model = User
        # Include standard fields plus our custom phone_number field
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number',)

    def save(self, commit=True):
        user = super().save(commit=False)
        # We enforce the role here just in case someone tampers with the form
        user.role = User.RoleChoices.EV_OWNER
        
        if commit:
            user.save()
        return user
    
    # Add this to the bottom of accounts/forms.py

class AdminUserCreationForm(UserCreationForm):
    # Limit choices to what the Admin is allowed to create
    ROLE_CHOICES = (
        (User.RoleChoices.STATION_OPERATOR, 'Charging Station Operator'),
        (User.RoleChoices.SERVICE_CENTER, 'Service Center'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Accounts created by Admin are automatically approved
        user.is_approved = True 
        if commit:
            user.save()
        return user
    
    # Add this to accounts/forms.py

class DeliveryPartnerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Force the role to Delivery Partner
        user.role = User.RoleChoices.DELIVERY_PARTNER
        # Auto-approve since they are being created by a trusted Service Center
        user.is_approved = True 
        if commit:
            user.save()
        return user