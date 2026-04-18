# delivery/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import role_required  # Using your original accounts decorator
from .models import DeliveryPartnerProfile, DeliveryOrder
from .forms import DeliveryProfileForm, UserProfileForm

@login_required
@role_required('DELIVERY_PARTNER')
def delivery_dashboard(request):
    # Gracefully get or create profile so it doesn't crash on first login
    partner, created = DeliveryPartnerProfile.objects.get_or_create(user=request.user)
    
    # Only show active orders on the main dashboard
    active_orders = DeliveryOrder.objects.filter(
        partner=partner, 
        status__in=['ASSIGNED', 'IN_TRANSIT']
    ).order_by('-assigned_at')
    
    completed_count = DeliveryOrder.objects.filter(partner=partner, status='DELIVERED').count()
    
    return render(request, 'delivery/dashboard.html', {
        'active_orders': active_orders,
        'completed_count': completed_count,
        'partner': partner
    })

@login_required
@role_required('DELIVERY_PARTNER')
def partner_profile_view(request):
    profile, created = DeliveryPartnerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserProfileForm(request.POST, instance=request.user)
        p_form = DeliveryProfileForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Delivery profile updated successfully.')
            return redirect('delivery_dashboard')
    else:
        u_form = UserProfileForm(instance=request.user)
        p_form = DeliveryProfileForm(instance=profile)
        
    return render(request, 'delivery/profile.html', {'u_form': u_form, 'p_form': p_form})

@login_required
@role_required('DELIVERY_PARTNER')
def update_delivery_status(request, order_id, new_status):
    order = get_object_or_404(DeliveryOrder, id=order_id, partner__user=request.user)
    
    # Security: Ensure they can only update to valid states
    valid_statuses = ['IN_TRANSIT', 'DELIVERED', 'FAILED']
    if new_status in valid_statuses:
        order.status = new_status
        if new_status == 'DELIVERED':
            order.delivered_at = timezone.now()
        order.save()
        messages.success(request, f"Order #{order.id} marked as {order.get_status_display()}.")
    
    return redirect('delivery_dashboard')

@login_required
@role_required('DELIVERY_PARTNER')
def delivery_history(request):
    partner, created = DeliveryPartnerProfile.objects.get_or_create(user=request.user)
    
    # Show only past orders (Completed or Failed)
    history = DeliveryOrder.objects.filter(
        partner=partner, 
        status__in=['DELIVERED', 'FAILED']
    ).order_by('-assigned_at')
    
    return render(request, 'delivery/history.html', {'history': history})