from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import date

from accounts.decorators import role_required
from bookings.models import Booking 
from .models import ChargingStation, Charger
from .forms import StationProfileForm, ChargerForm
# --- OPERATOR VIEWS ---

@login_required
@role_required('STATION_OPERATOR')
def operator_dashboard(request):
    # Try to get the station associated with the operator
    station = getattr(request.user, 'station_profile', None)
    chargers = station.chargers.all() if station else []
    
    context = {
        'station': station,
        'chargers': chargers,
    }
    
    # If station exists, add analytics
    if station:
        today = date.today()
        todays_bookings = Booking.objects.filter(charger__station=station, start_time__date=today)
        
        context.update({
            'today_bookings_count': todays_bookings.count(),
            'daily_revenue': sum(b.total_cost for b in todays_bookings if b.status == 'COMPLETED'),
            'pending_bookings': todays_bookings.filter(status='PENDING'),
        })
        
    return render(request, 'station/dashboard.html', context)

@login_required
@role_required('STATION_OPERATOR')
def station_profile(request):
    # This handles both setup and edit
    station, created = ChargingStation.objects.get_or_create(operator=request.user)
    
    if request.method == 'POST':
        form = ChargingStationProfileForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            messages.success(request, "Station profile updated successfully!")
            return redirect('operator_dashboard')
    else:
        form = ChargingStationProfileForm(instance=station)
        
    return render(request, 'station/station_profile.html', {'form': form, 'station': station})

@login_required
@role_required('STATION_OPERATOR')
def charger_list(request):
    station = getattr(request.user, 'station_profile', None)
    if not station:
        messages.warning(request, 'Please set up your station profile first.')
        return redirect('station_profile')
        
    chargers = station.chargers.all()
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


# --- EV OWNER VIEWS ---

@login_required
@role_required('EV_OWNER')
def browse_stations(request):
    stations_list = ChargingStation.objects.filter(is_active=True).order_by('name')
    
    # SEARCH
    search_query = request.GET.get('search', '')
    if search_query:
        stations_list = stations_list.filter(
            Q(name__icontains=search_query) | 
            Q(chargers__connector_type__icontains=search_query)
        ).distinct()
        
    # FILTER
    min_power = request.GET.get('min_power', '')
    if min_power and min_power.isdigit():
        stations_list = stations_list.filter(chargers__power_kw__gte=int(min_power)).distinct()

    # PAGINATION
    paginator = Paginator(stations_list, 10)
    page = request.GET.get('page')
    
    try:
        stations = paginator.page(page)
    except PageNotAnInteger:
        stations = paginator.page(1)
    except EmptyPage:
        stations = paginator.page(paginator.num_pages)

    return render(request, 'station/browse_stations.html', {
        'stations': stations,
        'search_query': search_query,
        'min_power': min_power,
    })