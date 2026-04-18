# service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import ServiceCenter, Appointment, Inventory
from .forms import ServiceCenterProfileForm, InventoryForm

@login_required
@role_required('SERVICE_CENTER')
def service_dashboard(request):
    center = getattr(request.user, 'service_center_profile', None)
    appointments = Appointment.objects.filter(service_center=center) if center else []
    inventory = Inventory.objects.filter(service_center=center) if center else []
    
    # Calculate low stock alerts natively in Python
    low_stock_items = [item for item in inventory if item.stock_quantity <= item.reorder_threshold]
    
    context = {
        'center': center,
        'appointments': appointments,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'service/dashboard.html', context)

@login_required
@role_required('SERVICE_CENTER')
def center_profile_view(request):
    center, created = ServiceCenter.objects.get_or_create(manager=request.user)
    
    if request.method == 'POST':
        form = ServiceCenterProfileForm(request.POST, instance=center)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service Center profile updated successfully.')
            return redirect('service_dashboard')
    else:
        form = ServiceCenterProfileForm(instance=center)
        
    return render(request, 'service/profile.html', {'form': form})

@login_required
@role_required('SERVICE_CENTER')
def appointment_list(request):
    center = getattr(request.user, 'service_center_profile', None)
    if not center:
        messages.warning(request, 'Please complete your Service Center profile first.')
        return redirect('center_profile')
        
    appointments = Appointment.objects.filter(service_center=center).order_by('scheduled_time')
    return render(request, 'service/appointments.html', {'appointments': appointments})

@login_required
@role_required('SERVICE_CENTER')
def update_appointment_status(request, pk, new_status):
    center = getattr(request.user, 'service_center_profile', None)
    appointment = get_object_or_404(Appointment, pk=pk, service_center=center)
    
    valid_statuses = dict(Appointment.StatusChoices.choices).keys()
    if new_status in valid_statuses:
        appointment.status = new_status
        appointment.save()
        messages.success(request, f'Repair status updated to {appointment.get_status_display()}.')
    
    return redirect('appointment_list')

@login_required
@role_required('SERVICE_CENTER')
def inventory_list(request):
    center = getattr(request.user, 'service_center_profile', None)
    if not center:
        messages.warning(request, 'Please complete your Service Center profile first.')
        return redirect('center_profile')
        
    inventory = Inventory.objects.filter(service_center=center)
    return render(request, 'service/inventory.html', {'inventory': inventory})

@login_required
@role_required('SERVICE_CENTER')
def inventory_create(request):
    center = get_object_or_404(ServiceCenter, manager=request.user)
    
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.service_center = center
            item.save()
            messages.success(request, 'Part added to inventory.')
            return redirect('inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'service/inventory_form.html', {'form': form, 'action': 'Add'})

from accounts.forms import DeliveryPartnerCreationForm

@login_required
@role_required('SERVICE_CENTER')
def create_delivery_partner(request):
    if request.method == 'POST':
        form = DeliveryPartnerCreationForm(request.POST)
        if form.is_valid():
            partner = form.save()
            messages.success(request, f"Delivery Partner '{partner.username}' account created successfully.")
            return redirect('service_dashboard')
    else:
        form = DeliveryPartnerCreationForm()
        
    return render(request, 'service/create_partner.html', {'form': form})

# Add this to service/views.py
from accounts.models import User
from notifications.models import Notification
from .forms import AppointmentBookingForm

@login_required
@role_required('EV_OWNER')
def owner_service_dashboard(request):
    appointments = Appointment.objects.filter(vehicle__user=request.user).order_by('-scheduled_time')
    service_centers = ServiceCenter.objects.all()
    return render(request, 'service/owner_service_dashboard.html', {
        'appointments': appointments,
        'centers': service_centers
    })

@login_required
@role_required('EV_OWNER')
def book_service(request, center_id):
    center = get_object_or_404(ServiceCenter, id=center_id)
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.service_center = center
            appointment.save()
            messages.success(request, f"Repair appointment booked at {center.name}!")
            return redirect('owner_service_dashboard')
    else:
        form = AppointmentBookingForm(request.user)
        
    return render(request, 'service/book_service.html', {'form': form, 'center': center})

@login_required
@role_required('EV_OWNER')
def trigger_sos(request):
    if request.method == 'POST':
        # Find all Admins and Service Centers to alert them
        emergency_contacts = User.objects.filter(role__in=['ADMIN', 'SERVICE_CENTER'])
        
        for contact in emergency_contacts:
            Notification.objects.create(
                user=contact,
                title="🚨 EMERGENCY SOS TRIGGERED",
                message=f"EV Owner {request.user.get_full_name() or request.user.username} requires immediate roadside assistance! Contact: {request.user.phone_number}"
            )
            
        messages.success(request, "SOS Alert broadcasted to all nearby Service Centers and Admins. Help is on the way.")
    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))

# Add these imports at the top of service/views.py if missing
from django.db.models import Count
from delivery.models import DeliveryOrder, DeliveryPartnerProfile
from .models import WarrantyClaim

# --- ORDERS MANAGEMENT ---
@login_required
@role_required('SERVICE_CENTER')
def manage_orders(request):
    center = get_object_or_404(ServiceCenter, manager=request.user)
    
    # Simple form handling to assign an order to a Delivery Partner
    if request.method == 'POST':
        partner_id = request.POST.get('partner_id')
        destination = request.POST.get('destination_address')
        
        if partner_id and destination:
            partner = get_object_or_404(DeliveryPartnerProfile, id=partner_id)
            DeliveryOrder.objects.create(
                partner=partner,
                destination_address=destination,
                status='ASSIGNED'
            )
            messages.success(request, f"Part order dispatched to {partner.user.username}.")
            return redirect('manage_orders')

    orders = DeliveryOrder.objects.all().order_by('-assigned_at')[:50] # Show recent platform orders
    partners = DeliveryPartnerProfile.objects.filter(is_available=True)
    
    return render(request, 'service/orders.html', {'orders': orders, 'partners': partners})


# --- WARRANTY VALIDATION ---
@login_required
@role_required('SERVICE_CENTER')
def warranty_list(request):
    center = get_object_or_404(ServiceCenter, manager=request.user)
    claims = WarrantyClaim.objects.filter(service_center=center).order_by('-created_at')
    return render(request, 'service/warranty.html', {'claims': claims})

@login_required
@role_required('SERVICE_CENTER')
def update_warranty_status(request, pk, new_status):
    center = get_object_or_404(ServiceCenter, manager=request.user)
    claim = get_object_or_404(WarrantyClaim, pk=pk, service_center=center)
    
    if new_status in dict(WarrantyClaim.StatusChoices.choices).keys():
        claim.status = new_status
        claim.save()
        messages.success(request, f"Warranty claim marked as {claim.get_status_display()}.")
        
    return redirect('warranty_list')


# --- REPORTS & ANALYTICS ---
@login_required
@role_required('SERVICE_CENTER')
def service_reports(request):
    center = get_object_or_404(ServiceCenter, manager=request.user)
    
    # Calculate performance analytics
    total_completed_repairs = Appointment.objects.filter(service_center=center, status='COMPLETED').count()
    approved_warranties = WarrantyClaim.objects.filter(service_center=center, status='APPROVED').count()
    
    # Group repairs by issue type to see what breaks most often
    issue_analytics = Appointment.objects.filter(service_center=center).values('issue_description').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'total_completed_repairs': total_completed_repairs,
        'approved_warranties': approved_warranties,
        'issue_analytics': issue_analytics,
    }
    return render(request, 'service/reports.html', context)