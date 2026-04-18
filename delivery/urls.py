# delivery/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('profile/', views.partner_profile_view, name='partner_profile'),
    path('history/', views.delivery_history, name='delivery_history'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_delivery_status, name='update_delivery_status'),
]