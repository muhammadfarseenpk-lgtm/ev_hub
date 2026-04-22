from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from datetime import date

from accounts.decorators import role_required
from owner.models import StationBooking # Using our correct booking model
from .models import ChargingStation, Charger, RevenueRecord
from .forms import StationProfileForm, ChargerForm

# --- OPERATOR DASHBOARD & PROFILE ---

@login_required
@role_required('STATION_OPERATOR')
def operator_dashboard(request):
    station = getattr(request.user, 'operated_station', None)
    chargers = station.chargers.all() if station else []
    
    context = {
        'station': station,
        'chargers': chargers,
    }
    
    if station:
        today = date.today()
        # Fetch today's bookings for this station
        todays_bookings = StationBooking.objects.filter(station=station, date=today)
        
        context.update({
            'today_bookings_count': todays_bookings.count(),
            'daily_revenue': sum(b.estimated_cost for b in todays_bookings if b.status == 'completed'),
            'pending_bookings': todays_bookings.filter(status='pending'),
            'recent_activity': StationBooking.objects.filter(station=station).order_by('-created_at')[:5]
        })
        
    return render(request, 'station/dashboard.html', context)

@login_required
@role_required('STATION_OPERATOR')
def station_profile(request):
    station, created = ChargingStation.objects.get_or_create(operator=request.user)
    
    if request.method == 'POST':
        form = StationProfileForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            messages.success(request, 'Station profile updated!')
            return redirect('operator_dashboard')
    else:
        form = StationProfileForm(instance=station)
    return render(request, 'station/station_profile.html', {'form': form, 'station': station})

# --- CHARGER MANAGEMENT ---

@login_required
@role_required('STATION_OPERATOR')
def charger_list(request):
    station = getattr(request.user, 'operated_station', None)
    if not station:
        messages.warning(request, 'Please set up your station profile first.')
        return redirect('station_profile')
        
    chargers_list = station.chargers.all().order_by('charger_id')
    paginator = Paginator(chargers_list, 10) # Added Pagination
    chargers = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'station/charger_list.html', {'chargers': chargers, 'station': station})

@login_required
@role_required('STATION_OPERATOR')
def charger_create(request):
    station = get_object_or_404(ChargingStation, operator=request.user)
    
    if request.method == 'POST':
        form = ChargerForm(request.POST)
        if form.is_valid():
            charger = form.save(commit=False)
            charger.station = station
            charger.save()
            messages.success(request, 'Charger added successfully.')
            return redirect('charger_list')
    else:
        form = ChargerForm()
    return render(request, 'station/charger_form.html', {'form': form, 'action': 'Add'})

@login_required
@role_required('STATION_OPERATOR')
def charger_update(request, pk):
    station = get_object_or_404(ChargingStation, operator=request.user)
    charger = get_object_or_404(Charger, pk=pk, station=station)
    
    if request.method == 'POST':
        form = ChargerForm(request.POST, instance=charger)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charger updated successfully.')
            return redirect('charger_list')
    else:
        form = ChargerForm(instance=charger)
    return render(request, 'station/charger_form.html', {'form': form, 'action': 'Edit'})

@login_required
@role_required('STATION_OPERATOR')
def charger_delete(request, pk):
    station = get_object_or_404(ChargingStation, operator=request.user)
    charger = get_object_or_404(Charger, pk=pk, station=station)
    
    if request.method == 'POST':
        charger.delete()
        messages.success(request, 'Charger removed successfully.')
        return redirect('charger_list')
        
    return render(request, 'station/charger_confirm_delete.html', {'charger': charger})

# --- BOOKING MANAGEMENT ---

@login_required
@role_required('STATION_OPERATOR')
def operator_booking_list(request):
    station = getattr(request.user, 'operated_station', None)
    if not station:
        messages.warning(request, "Please set up your station first.")
        return redirect('station_profile')
    
    bookings_list = StationBooking.objects.filter(station=station).order_by('-date', '-start_time')
    
    # Optional status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings_list = bookings_list.filter(status=status_filter)
        
    paginator = Paginator(bookings_list, 15) # Added Pagination
    bookings = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'station/operator_bookings.html', {'bookings': bookings, 'status_filter': status_filter})

@login_required
@role_required('STATION_OPERATOR')
def update_booking_status(request, booking_id, new_status):
    station = getattr(request.user, 'operated_station', None)
    booking = get_object_or_404(StationBooking, id=booking_id, station=station)
    
    valid_statuses = ['approved', 'rejected', 'completed']
    if new_status in valid_statuses:
        # Prevent duplicating revenue if they accidentally click "Complete" twice
        if new_status == 'completed' and booking.status != 'completed':
            RevenueRecord.objects.create(
                station=station, 
                booking_id=booking.id, 
                amount=booking.estimated_cost
            )
            
        booking.status = new_status
        booking.save()
        messages.success(request, f"Booking from {booking.user.username} marked as {booking.get_status_display()}.")
        
    return redirect(request.META.get('HTTP_REFERER', 'operator_booking_list'))

# --- REPORTS & ANALYTICS ---

@login_required
@role_required('STATION_OPERATOR')
def operator_reports(request):
    station = getattr(request.user, 'operated_station', None)
    if not station:
        return redirect('station_profile')
        
    # Aggregate Revenue from our new RevenueRecord table
    revenue_records = RevenueRecord.objects.filter(station=station)
    total_revenue = sum(r.amount for r in revenue_records)
    
    # SAFE FALLBACK: Just list the chargers for now to prevent a crash.
    # We can add the 'usage_count' back later if you decide to link 
    # bookings to specific chargers in your owner models!
    charger_analytics = Charger.objects.filter(station=station)
    
    context = {
        'total_revenue': total_revenue,
        'completed_count': revenue_records.count(),
        'charger_analytics': charger_analytics,
        'revenue_records': revenue_records.order_by('-date')[:10]
    }
    return render(request, 'station/operator_reports.html', context)