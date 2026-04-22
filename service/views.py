from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Sum
from datetime import date

# Adjust these imports if your decorators are in a different file!
from accounts.decorators import role_required 
from .models import ServiceCenter, ServiceAppointment, InventoryItem, PartOrder, ServiceRevenue, WarrantyClaim
from .forms import ServiceCenterForm, InventoryItemForm, PartOrderForm

# --- DASHBOARD & PROFILE ---

@login_required
@role_required('SERVICE_CENTER')
def service_dashboard(request):
    center = getattr(request.user, 'service_center', None)
    
    if not center:
        return render(request, 'service/dashboard.html', {'center': None})

    # Core Metrics
    appointments = ServiceAppointment.objects.filter(center=center)
    low_stock_items = InventoryItem.objects.filter(center=center, quantity__lt=F('threshold'))
    
    context = {
        'center': center,
        'total_appointments': appointments.count(),
        'in_progress': appointments.filter(status='in_progress').count(),
        'completed': appointments.filter(status='completed').count(),
        'low_stock_count': low_stock_items.count(),
        'recent_requests': appointments.order_by('-created_at')[:5],
        'low_stock_items': low_stock_items[:5],
    }
    return render(request, 'service/dashboard.html', context)

@login_required
@role_required('SERVICE_CENTER')
def service_profile(request):
    center, created = ServiceCenter.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ServiceCenterForm(request.POST, instance=center)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service Center profile updated successfully!')
            return redirect('service_dashboard')
    else:
        form = ServiceCenterForm(instance=center)
        
    return render(request, 'service/service_profile.html', {'form': form, 'center': center})

# --- APPOINTMENT & REPAIR MANAGEMENT ---

@login_required
@role_required('SERVICE_CENTER')
def appointment_list(request):
    center = getattr(request.user, 'service_center', None)
    if not center:
        messages.warning(request, "Please set up your service profile first.")
        return redirect('service_profile')

    appointments_qs = ServiceAppointment.objects.filter(center=center).order_by('-date', '-time')
    
    # Filter functionality
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments_qs = appointments_qs.filter(status=status_filter)

    paginator = Paginator(appointments_qs, 15)
    appointments = paginator.get_page(request.GET.get('page'))

    # Change this line:
    return render(request, 'service/appointments.html', {
        'appointments': appointments, 
        'status_filter': status_filter
    })

@login_required
@role_required('SERVICE_CENTER')
def update_appointment_status(request, appointment_id, new_status):
    center = getattr(request.user, 'service_center', None)
    appointment = get_object_or_404(ServiceAppointment, id=appointment_id, center=center)
    
    valid_statuses = [choice[0] for choice in ServiceAppointment.STATUS_CHOICES]
    
    if new_status in valid_statuses:
        # Business Logic: Generate Revenue on Completion
        if new_status == 'completed' and appointment.status != 'completed':
            ServiceRevenue.objects.get_or_create(
                center=center, 
                appointment=appointment, 
                defaults={'amount': appointment.estimated_cost}
            )
            
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Repair for {appointment.vehicle.make} marked as {appointment.get_status_display()}.")
        
    return redirect(request.META.get('HTTP_REFERER', 'appointment_list'))

# --- INVENTORY & ORDERS ---

@login_required
@role_required('SERVICE_CENTER')
def inventory_list(request):
    center = getattr(request.user, 'service_center', None)
    if not center:
        return redirect('service_profile')

    inventory_qs = InventoryItem.objects.filter(center=center).order_by('part_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        inventory_qs = inventory_qs.filter(part_name__icontains=search_query)

    paginator = Paginator(inventory_qs, 20)
    inventory = paginator.get_page(request.GET.get('page'))

    return render(request, 'service/inventory_list.html', {
        'inventory': inventory,
        'search_query': search_query
    })

@login_required
@role_required('SERVICE_CENTER')
def manage_inventory_item(request, item_id=None):
    center = get_object_or_404(ServiceCenter, user=request.user)
    
    if item_id:
        item = get_object_or_404(InventoryItem, id=item_id, center=center)
        action = "Edit"
    else:
        item = None
        action = "Add"

    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.center = center
            new_item.save()
            messages.success(request, f"Inventory item {action.lower()}ed successfully.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)

    return render(request, 'service/inventory_form.html', {'form': form, 'action': action})

@login_required
@role_required('SERVICE_CENTER')
def order_list(request):
    center = getattr(request.user, 'service_center', None)
    orders_qs = PartOrder.objects.filter(item__center=center).order_by('-created_at')
    
    paginator = Paginator(orders_qs, 15)
    orders = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'service/order_list.html', {'orders': orders})

@login_required
@role_required('SERVICE_CENTER')
def create_order(request, item_id):
    center = get_object_or_404(ServiceCenter, user=request.user)
    item = get_object_or_404(InventoryItem, id=item_id, center=center)
    
    if request.method == 'POST':
        form = PartOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.item = item
            order.save()
            
            # Business Logic: Auto-restock if marked delivered instantly
            if order.status == 'delivered':
                item.quantity = F('quantity') + order.quantity
                item.save()
                
            messages.success(request, f"Order placed for {item.part_name}.")
            return redirect('order_list')
    else:
        form = PartOrderForm(initial={'quantity': max(item.threshold - item.quantity, 1)})
        
    return render(request, 'service/order_form.html', {'form': form, 'item': item})

@login_required
@role_required('SERVICE_CENTER')
def update_order_status(request, order_id, new_status):
    center = getattr(request.user, 'service_center', None)
    order = get_object_or_404(PartOrder, id=order_id, item__center=center)
    
    valid_statuses = [choice[0] for choice in PartOrder.STATUS_CHOICES]
    
    if new_status in valid_statuses:
        # Business Logic: Increase stock upon delivery
        if new_status == 'delivered' and order.status != 'delivered':
            order.item.quantity = F('quantity') + order.quantity
            order.item.save()
            
        order.status = new_status
        order.save()
        messages.success(request, f"Order status updated to {order.get_status_display()}.")
        
    return redirect('order_list')

# --- REPORTS & ANALYTICS ---

@login_required
@role_required('SERVICE_CENTER')
def service_reports(request):
    center = getattr(request.user, 'service_center', None)
    if not center:
        return redirect('service_profile')

    # Match the variables your reports.html is asking for
    total_completed_repairs = ServiceAppointment.objects.filter(center=center, status='completed').count()
    approved_warranties = WarrantyClaim.objects.filter(appointment__center=center, status='approved').count()
    
    # Group issues to see what breaks most often
    issue_analytics = ServiceAppointment.objects.filter(center=center).values('issue_description').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'total_completed_repairs': total_completed_repairs,
        'approved_warranties': approved_warranties,
        'issue_analytics': issue_analytics,
    }
    # Note: Make sure the template name matches the file you uploaded!
    return render(request, 'service/reports.html', context)
from django.db.models import Count # Make sure to add this import at the top of views.py!

@login_required
@role_required('SERVICE_CENTER')
def warranty_list(request):
    center = getattr(request.user, 'service_center', None)
    if not center:
        return redirect('service_profile')
        
    warranties = WarrantyClaim.objects.filter(appointment__center=center).order_by('-created_at')
    return render(request, 'service/warranties.html', {'warranties': warranties})

@login_required
@role_required('SERVICE_CENTER')
def update_warranty_status(request, claim_id, new_status):
    center = getattr(request.user, 'service_center', None)
    claim = get_object_or_404(WarrantyClaim, id=claim_id, appointment__center=center)
    
    if new_status in ['approved', 'rejected']:
        claim.status = new_status
        claim.save()
        messages.success(request, f"Warranty claim marked as {claim.get_status_display()}.")
        
    return redirect('warranty_list')