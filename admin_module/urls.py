# admin_module/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='admin_users'),
    path('users/<int:user_id>/<str:action>/', views.toggle_user_status, name='toggle_user_status'),
    path('roles/create/', views.role_management, name='admin_create_role'),
    path('complaints/', views.complaint_list, name='admin_complaints'),
    path('complaints/<int:pk>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('logs/', views.activity_logs, name='admin_logs'),
]