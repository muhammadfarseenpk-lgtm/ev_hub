from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.operator_dashboard, name='operator_dashboard'),
    
    # Station Profile 
    path('profile/', views.station_profile, name='station_profile'),
    
    # Charger Management
    path('chargers/', views.charger_list, name='charger_list'),
    path('chargers/add/', views.charger_create, name='charger_create'),
    path('chargers/<int:pk>/edit/', views.charger_update, name='charger_update'),
    path('chargers/<int:pk>/delete/', views.charger_delete, name='charger_delete'),
    
    # Booking Management
    path('bookings/', views.operator_booking_list, name='operator_booking_list'),
    path('bookings/<int:booking_id>/status/<str:new_status>/', views.update_booking_status, name='update_booking_status'),
    
    # Reports
    path('reports/', views.operator_reports, name='operator_reports'),
]