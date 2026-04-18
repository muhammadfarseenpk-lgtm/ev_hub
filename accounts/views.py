# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EVOwnerRegistrationForm

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