from django.urls import path
from . import views

urlpatterns = [
    path('', views.delivery_dashboard, name='delivery_dashboard'),
    path('history/', views.delivery_history, name='delivery_history'),
    path('task/<int:task_id>/status/<str:new_status>/', views.update_task_status, name='update_task_status'),
    path('task/<int:task_id>/route/', views.route_guidance, name='route_guidance'),
    path('profile/', views.partner_profile_view, name='partner_profile'),
    # Assuming partner_profile is already here from your previous step
    # path('profile/', views.partner_profile, name='partner_profile'), 
]