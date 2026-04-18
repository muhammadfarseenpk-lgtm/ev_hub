# owner/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from accounts.decorators import role_required
from .models import Vehicle, Wallet
from .forms import VehicleForm, UserProfileForm

@login_required
@role_required('EV_OWNER')
def owner_dashboard(request):
    vehicles = request.user.vehicles.all()
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    context = {
        'vehicles': vehicles,
        'wallet': wallet,
    }
    return render(request, 'owner/dashboard.html', context)

@login_required
@role_required('EV_OWNER')
def vehicle_list(request):
    vehicles = request.user.vehicles.all()
    return render(request, 'owner/vehicle_list.html', {'vehicles': vehicles})

@login_required
@role_required('EV_OWNER')
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            vehicle.save()
            messages.success(request, 'Vehicle registered successfully.')
            return redirect('owner_vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'owner/vehicle_form.html', {'form': form, 'action': 'Add'})

@login_required
@role_required('EV_OWNER')
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully.')
            return redirect('owner_vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'owner/vehicle_form.html', {'form': form, 'action': 'Edit'})

@login_required
@role_required('EV_OWNER')
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle removed from your account.')
        return redirect('owner_vehicle_list')
    return render(request, 'owner/vehicle_confirm_delete.html', {'vehicle': vehicle})

@login_required
@role_required('EV_OWNER')
def profile_view(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            p_form = UserProfileForm(request.POST, instance=request.user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('owner_profile')
        elif 'change_password' in request.POST:
            pwd_form = PasswordChangeForm(request.user, request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated.')
                return redirect('owner_profile')
            else:
                messages.error(request, 'Please correct the error below.')
    
    p_form = UserProfileForm(instance=request.user)
    pwd_form = PasswordChangeForm(request.user)
    
    return render(request, 'owner/profile.html', {'p_form': p_form, 'pwd_form': pwd_form})