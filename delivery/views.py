# delivery/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import role_required  # Using your original accounts decorator
from .models import DeliveryPartnerProfile, DeliveryTask
from .forms import DeliveryProfileForm, UserProfileForm

@login_required
@role_required('DELIVERY_PARTNER')
def delivery_dashboard(request):
    # Gracefully get or create profile so it doesn't crash on first login
    profile, created = DeliveryPartnerProfile.objects.get_or_create(user=request.user)
    
    # Only show active orders on the main dashboard (matches DeliveryTask StatusChoices)
    active_tasks = DeliveryTask.objects.filter(
        partner=profile, 
        status__in=['ASSIGNED', 'PICKED_UP']
    ).order_by('-assigned_at')
    
    completed_count = DeliveryTask.objects.filter(partner=profile, status='DELIVERED').count()
    
    return render(request, 'delivery/dashboard.html', {
        'tasks': active_tasks, # Template expects 'tasks'
        'completed_count': completed_count,
        'partner': profile
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
        
    # Passing 'form' as well so {{ form.as_p }} in your template doesn't crash
    return render(request, 'delivery/profile.html', {
        'u_form': u_form, 
        'p_form': p_form, 
        'form': p_form 
    })

@login_required
@role_required('DELIVERY_PARTNER')
def update_task_status(request, task_id, new_status):
    profile = get_object_or_404(DeliveryPartnerProfile, user=request.user)
    task = get_object_or_404(DeliveryTask, id=task_id, partner=profile)
    
    # Security: Ensure they can only update to valid states
    valid_statuses = ['PICKED_UP', 'DELIVERED', 'FAILED']
    if new_status in valid_statuses:
        task.status = new_status
        if new_status == 'DELIVERED':
            task.completed_at = timezone.now()
        task.save()
        messages.success(request, f"Task #{task.id} marked as {task.get_status_display()}.")
    
    return redirect('delivery_dashboard')

@login_required
@role_required('DELIVERY_PARTNER')
def route_guidance(request, task_id):
    profile = getattr(request.user, 'delivery_profile', None)
    task = get_object_or_404(DeliveryTask, id=task_id, partner=profile)
    return render(request, 'delivery/route_guidance.html', {'task': task})

@login_required
@role_required('DELIVERY_PARTNER')
def delivery_history(request):
    profile, created = DeliveryPartnerProfile.objects.get_or_create(user=request.user)
    
    # Show only past orders (Completed or Failed)
    history = DeliveryTask.objects.filter(
        partner=profile, 
        status__in=['DELIVERED', 'FAILED']
    ).order_by('-completed_at') # Order by completion date instead of assigned
    
    return render(request, 'delivery/history.html', {'tasks': history}) # Template expects 'tasks'