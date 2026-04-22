from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Profile
    path('', views.service_dashboard, name='service_dashboard'),
    path('profile/', views.service_profile, name='service_profile'),
    
    # Appointments & Repairs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/status/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
    
    # Inventory Management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.manage_inventory_item, name='inventory_create'),
    path('inventory/<int:item_id>/edit/', views.manage_inventory_item, name='inventory_edit'),
    
    # Part Orders
    path('orders/', views.order_list, name='order_list'),
    path('inventory/<int:item_id>/order/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/status/<str:new_status>/', views.update_order_status, name='update_order_status'),
    
    # Reports
    path('reports/', views.service_reports, name='service_reports'),
    
    # Warranty Management
    path('warranties/', views.warranty_list, name='warranty_list'),
    path('warranties/<int:claim_id>/status/<str:new_status>/', views.update_warranty_status, name='update_warranty_status'),
]