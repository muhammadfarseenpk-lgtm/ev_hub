# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EVOwnerRegistrationForm
from .decorators import role_required
from .forms import EVOwnerRegistrationForm, AdminUserCreationForm, DeliveryPartnerCreationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')
        
    if request.method == 'POST':
        form = EVOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optional Email Verification logic would trigger here
            login(request, user)
            messages.success(request, "Registration successful. Welcome to the EV Platform!")
            return redirect('dashboard_router')
    else:
        form = EVOwnerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_approved:
                messages.error(request, "Your account is pending approval.")
                return redirect('login')
                
            login(request, user)
            return redirect('dashboard_router')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('login')

@login_required
def dashboard_router(request):
    """The core traffic controller for RBAC."""
    role = request.user.role
    
    # These URL names will be defined in their respective app's urls.py files
    if role == 'ADMIN':
        return redirect('admin_dashboard')
    elif role == 'EV_OWNER':
        return redirect('owner_dashboard')
    elif role == 'STATION_OPERATOR':
        return redirect('operator_dashboard')
    elif role == 'SERVICE_CENTER':
        return redirect('service_dashboard')
    elif role == 'DELIVERY_PARTNER':
        return redirect('delivery_dashboard')
        
    logout(request)
    return redirect('login')

# accounts/views.py

@login_required
@role_required('ADMIN')
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Successfully created {user.get_role_display()} account.")
            
            # ---> CHANGE THIS LINE TO MATCH BELOW <---
            return redirect('dashboard_router') 
            
    else:
        form = AdminUserCreationForm()
    return render(request, 'accounts/admin_create_user.html', {'form': form})
# Add this to accounts/views.py

@login_required
@role_required('SERVICE_CENTER')
def center_create_delivery(request):
    if request.method == 'POST':
        form = DeliveryPartnerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Successfully registered Delivery Partner: {user.username}.")
            return redirect('dashboard_router') # Routes back to the Service Center dashboard
    else:    form = DeliveryPartnerCreationForm()
        
    return render(request, 'accounts/center_create_delivery.html', {'form': form})