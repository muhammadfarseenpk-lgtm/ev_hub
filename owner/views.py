from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from accounts.decorators import role_required

# Import Models
from .models import Vehicle, Wallet, StationBooking, ServiceRequest, EmergencySOS, Notification
from station.models import ChargingStation, StationReview
from service.models import ServiceAppointment

# Import Forms
from .forms import VehicleForm, StationBookingForm, ServiceRequestForm, UserProfileForm



# ==========================================
# 1. DASHBOARD
# ==========================================
@login_required
@role_required('EV_OWNER')
def owner_dashboard(request):
    # Fetch/Create Wallet
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Fetch Vehicles
    vehicles = request.user.vehicles.all()
    
    # SMART REMINDER LOGIC: Find cars that need maintenance
    maintenance_alerts = []
    for car in vehicles:
        # Check battery_health (or fallback to battery_level if health isn't defined)
        if getattr(car, 'battery_health', 100) < 85: 
            maintenance_alerts.append({
                'car': car,
                'message': f"Battery health dropped to {getattr(car, 'battery_health', 100)}%. A diagnostic is recommended."
            })

    # Upcoming Bookings (Future/Today, sorted by nearest date)
    today = timezone.now().date()
    upcoming_bookings = StationBooking.objects.select_related('station').filter(
        user=request.user, 
        date__gte=today,
        status__in=['pending', 'approved']
    ).order_by('date', 'start_time')[:5]

    # Recent Activity / Notifications (Last 5 actions)
    recent_activity = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'wallet': wallet,
        'vehicles': vehicles,
        'maintenance_alerts': maintenance_alerts,
        'upcoming_bookings': upcoming_bookings,
        'recent_activity': recent_activity
    }
    return render(request, 'owner/dashboard.html', context)


# ==========================================
# 2. VEHICLE MANAGEMENT
# ==========================================
@login_required
@role_required('EV_OWNER')
def vehicle_list(request):
    vehicle_qs = request.user.vehicles.all().order_by('-id')
    paginator = Paginator(vehicle_qs, 10) # Pagination: 10 per page
    page_number = request.GET.get('page')
    vehicles = paginator.get_page(page_number)
    
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


# ==========================================
# 3. STATION BROWSING & REVIEWS
# ==========================================
@login_required
@role_required('EV_OWNER')
def browse_stations(request):
    stations = ChargingStation.objects.all().order_by('name')
    
    # Search & Filter Logic
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        stations = stations.filter(Q(name__icontains=search_query) | Q(location__icontains=search_query))
    if status_filter:
        stations = stations.filter(status=status_filter)

    paginator = Paginator(stations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'owner/station_list.html', {
        'stations': page_obj, 
        'search_query': search_query,
        'status_filter': status_filter
    })

@login_required
@role_required('EV_OWNER')
def submit_review(request, station_id):
    station = get_object_or_404(ChargingStation, id=station_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        StationReview.objects.create(
            station=station,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, f"Thank you for reviewing {station.name}!")
        return redirect('browse_stations')
        
    return render(request, 'owner/submit_review.html', {'station': station})


# ==========================================
# 4. BOOKING SYSTEM
# ==========================================
@login_required
@role_required('EV_OWNER')
def booking_list(request):
    bookings = StationBooking.objects.select_related('station', 'vehicle').filter(user=request.user)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
        
    bookings = bookings.order_by('-date', '-start_time')
    paginator = Paginator(bookings, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'owner/booking_list.html', {'bookings': page_obj, 'status_filter': status_filter})

@login_required
@role_required('EV_OWNER')
def booking_manage(request, pk=None):
    booking = get_object_or_404(StationBooking, pk=pk, user=request.user) if pk else None

    if request.method == 'POST':
        form = StationBookingForm(request.POST, instance=booking, user=request.user)
        if form.is_valid():
            new_booking = form.save(commit=False)
            new_booking.user = request.user
            new_booking.status = 'pending' 
            new_booking.save()
            
            Notification.objects.create(
                user=request.user, 
                title="Booking Request Submitted", 
                message=f"Your booking at {new_booking.station.name} is pending approval."
            )
            
            messages.success(request, "Booking successfully created/rescheduled. Awaiting approval.")
            return redirect('booking_list')
    else:
        form = StationBookingForm(instance=booking, user=request.user)
    return render(request, 'owner/booking_form.html', {'form': form})

@login_required
@role_required('EV_OWNER')
def booking_cancel(request, pk):
    booking = get_object_or_404(StationBooking, pk=pk, user=request.user)
    if booking.status in ['pending', 'approved']:
        booking.status = 'cancelled'
        booking.save()
        Notification.objects.create(user=request.user, title="Booking Cancelled", message=f"Booking at {booking.station.name} cancelled.")
        messages.success(request, "Booking cancelled.")
    else:
        messages.error(request, "Cannot cancel a completed or already cancelled booking.")
    return redirect('booking_list')


# ==========================================
# 5. WALLET SYSTEM
# ==========================================
@login_required
@role_required('EV_OWNER')
def add_funds(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount > 0:
                wallet.balance += amount
                wallet.save()
                Notification.objects.create(user=request.user, title="Funds Added", message=f"${amount} added to your wallet.")
                messages.success(request, f"${amount} added to your wallet.")
            else:
                messages.error(request, "Please enter a valid amount.")
        except ValueError:
            messages.error(request, "Invalid amount entered.")
        return redirect('owner_dashboard')
    return render(request, 'owner/wallet_add.html', {'wallet': wallet})


# ==========================================
# 6. SERVICE & REPAIRS
# ==========================================
@login_required
@role_required('EV_OWNER')
def owner_service_dashboard(request):
    # Fetch the ServiceRequests instead of Appointments
    repairs = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        repairs = repairs.filter(status=status_filter)
        
    return render(request, 'owner/repair_tracking.html', {'repairs': repairs, 'status_filter': status_filter})
@login_required
@role_required('EV_OWNER')
def service_request_create(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_req = form.save(commit=False)
            service_req.user = request.user
            if service_req.vehicle.user != request.user:
                messages.error(request, "Invalid vehicle selection.")
                return redirect('book_repair')
            service_req.save()
            Notification.objects.create(user=request.user, title="Service Request Sent", message="Your repair request is pending.")
            messages.success(request, "Service request submitted.")
            return redirect('owner_service_dashboard')
    else:
        form = ServiceRequestForm()
        form.fields['vehicle'].queryset = request.user.vehicles.all()
    return render(request, 'owner/service_form.html', {'form': form})


# ==========================================
# 7. EMERGENCY SOS
# ==========================================
@login_required
@role_required('EV_OWNER')
def trigger_sos(request):
    if request.method == 'POST':
        EmergencySOS.objects.create(user=request.user, status='active')
        Notification.objects.create(user=request.user, title="SOS Triggered", message="Emergency services have been alerted.")
        messages.error(request, "🚨 EMERGENCY SOS ACTIVATED. Stations and Centers have been notified.")
    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))


# ==========================================
# 8. PROFILE & NOTIFICATIONS
# ==========================================
@login_required
@role_required('EV_OWNER')
def profile_view(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            p_form = UserProfileForm(request.POST, instance=request.user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('profile_view')
        elif 'change_password' in request.POST:
            pwd_form = PasswordChangeForm(request.user, request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated.')
                return redirect('profile_view')
            else:
                messages.error(request, 'Please correct the error below.')
    
    p_form = UserProfileForm(instance=request.user)
    pwd_form = PasswordChangeForm(request.user)
    
    return render(request, 'owner/profile.html', {'p_form': p_form, 'pwd_form': pwd_form})

@login_required
@role_required('EV_OWNER')
def notifications_view(request):
    notes = Notification.objects.filter(user=request.user)
    notes.filter(is_read=False).update(is_read=True) # Auto mark as read when viewed
    paginator = Paginator(notes, 15)
    return render(request, 'owner/notifications.html', {'notifications': paginator.get_page(request.GET.get('page'))})

from django.contrib import admin
from .models import Wallet, Vehicle, StationBooking, ServiceRequest, EmergencySOS, Notification

# Registering models with customized list displays
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'last_updated')
    search_fields = ('user__username',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'user', 'make', 'model', 'battery_level')
    list_filter = ('make',)
    search_fields = ('registration_number', 'user__username')

@admin.register(StationBooking)
class StationBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'station', 'date', 'start_time', 'status')
    list_filter = ('status', 'date')
    
@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'service_center', 'status', 'created_at')
    list_filter = ('status',)

admin.site.register(EmergencySOS)
admin.site.register(Notification)