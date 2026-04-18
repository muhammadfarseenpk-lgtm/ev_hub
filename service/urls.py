# service/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_dashboard, name='service_dashboard'),
    path('profile/', views.center_profile_view, name='center_profile'),
    
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:pk>/status/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
    
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_create, name='inventory_create'),
    path('delivery-partners/create/', views.create_delivery_partner, name='create_delivery_partner'),
    path('my-repairs/', views.owner_service_dashboard, name='owner_service_dashboard'),
    path('book-repair/<int:center_id>/', views.book_service, name='book_service'),
    path('sos-emergency/', views.trigger_sos, name='trigger_sos'),
    path('orders/', views.manage_orders, name='manage_orders'),
    path('warranty/', views.warranty_list, name='warranty_list'),
    path('warranty/<int:pk>/status/<str:new_status>/', views.update_warranty_status, name='update_warranty_status'),
    path('reports/', views.service_reports, name='service_reports'),
    
]