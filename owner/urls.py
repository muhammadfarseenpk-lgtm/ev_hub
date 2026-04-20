from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    
    # Vehicle Management
    path('vehicles/', views.vehicle_list, name='owner_vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_add'),
    path('vehicles/edit/<int:pk>/', views.vehicle_update, name='vehicle_edit'),
    path('vehicles/delete/<int:pk>/', views.vehicle_delete, name='vehicle_delete'),
    
    # Station Browsing & Reviews
    path('stations/', views.browse_stations, name='browse_stations'),
    path('stations/<int:station_id>/review/', views.submit_review, name='submit_review'),
    
    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/new/', views.booking_manage, name='booking_create'),
    path('bookings/reschedule/<int:pk>/', views.booking_manage, name='booking_reschedule'),
    path('bookings/cancel/<int:pk>/', views.booking_cancel, name='booking_cancel'),
    
    # Wallet
    path('wallet/add/', views.add_funds, name='wallet_add_funds'),
    
    # Services & SOS
    path('service/my-repairs/', views.owner_service_dashboard, name='owner_service_dashboard'),
    path('service/request/', views.service_request_create, name='book_repair'),
    path('sos/trigger/', views.trigger_sos, name='trigger_sos'),
    
    # Profile & Notifications
    path('profile/', views.profile_view, name='profile_view'), 
    path('notifications/', views.notifications_view, name='notification_list'),
]