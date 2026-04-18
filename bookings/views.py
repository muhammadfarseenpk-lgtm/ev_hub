# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Booking
from station.models import Charger
from .forms import BookingForm

# --- EV OWNER VIEWS ---

@login_required
@role_required('EV_OWNER')
def owner_booking_list(request):
    bookings = request.user.bookings.all()
    return render(request, 'bookings/owner_list.html', {'bookings': bookings})

@login_required
@role_required('EV_OWNER')
def create_booking(request, charger_id):
    charger = get_object_or_404(Charger, id=charger_id, status='AVAILABLE')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Check for overlapping bookings
            start = form.cleaned_data['start_time']
            end = form.cleaned_data['end_time']
            overlap = Booking.objects.filter(
                charger=charger,
                status__in=['PENDING', 'APPROVED'],
                start_time__lt=end,
                end_time__gt=start
            ).exists()
            
            if overlap:
                messages.error(request, "This charger is already booked for that time slot.")
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.charger = charger
                # Calculate cost based on duration and dynamic price
                duration_hours = (end - start).total_seconds() / 3600
                booking.total_cost = float(duration_hours) * float(charger.dynamic_price_per_kwh)
                booking.save()
                messages.success(request, "Booking request sent to the station operator.")
                return redirect('owner_booking_list')
    else:
        form = BookingForm()
        
    return render(request, 'bookings/booking_form.html', {'form': form, 'charger': charger, 'action': 'Book'})

@login_required
@role_required('EV_OWNER')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status in ['PENDING', 'APPROVED']:
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "Cannot cancel a completed or already cancelled booking.")
    return redirect('owner_booking_list')


# --- STATION OPERATOR VIEWS ---

@login_required
@role_required('STATION_OPERATOR')
def operator_booking_list(request):
    station = getattr(request.user, 'station_profile', None)
    bookings = Booking.objects.filter(charger__station=station) if station else []
    return render(request, 'bookings/operator_list.html', {'bookings': bookings})

@login_required
@role_required('STATION_OPERATOR')
def update_booking_status(request, booking_id, action):
    station = getattr(request.user, 'station_profile', None)
    booking = get_object_or_404(Booking, id=booking_id, charger__station=station)
    
    if booking.status == 'PENDING':
        if action == 'approve':
            booking.status = 'APPROVED'
            messages.success(request, "Booking approved.")
        elif action == 'reject':
            booking.status = 'REJECTED'
            messages.success(request, "Booking rejected.")
        booking.save()
    return redirect('operator_booking_list')