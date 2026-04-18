# station/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.operator_dashboard, name='operator_dashboard'),
    
    # Station Profile (Merged logic: setup and edit are now one view)
    path('profile/', views.station_profile, name='station_profile'),
    
    # Charger Management
    path('chargers/', views.charger_list, name='charger_list'),
    path('chargers/add/', views.charger_create, name='charger_create'),
    path('chargers/<int:pk>/edit/', views.charger_update, name='charger_update'),
    
    # EV Owner Browsing
    path('browse/', views.browse_stations, name='browse_stations'),
]