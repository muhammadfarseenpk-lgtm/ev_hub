# owner/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.owner_dashboard, name='owner_dashboard'),
    path('vehicles/', views.vehicle_list, name='owner_vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='owner_vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.vehicle_update, name='owner_vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='owner_vehicle_delete'),
    path('profile/', views.profile_view, name='owner_profile'),
    path('', views.owner_dashboard, name='owner_dashboard'),
    path('vehicles/', views.vehicle_list, name='owner_vehicle_list'),
    path('my-repairs/', views.owner_service_dashboard, name='owner_service_dashboard'),
    path('station/<int:station_id>/review/', views.submit_review, name='submit_review'),
]