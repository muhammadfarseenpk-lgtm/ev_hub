# bookings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Owner URLs
    path('my-bookings/', views.owner_booking_list, name='owner_booking_list'),
    path('book/<int:charger_id>/', views.create_booking, name='create_booking'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Operator URLs
    path('station-requests/', views.operator_booking_list, name='operator_booking_list'),
    path('status/<int:booking_id>/<str:action>/', views.update_booking_status, name='update_booking_status'),
]