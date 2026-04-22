# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('router/', views.dashboard_router, name='dashboard_router'),
  # accounts/urls.py
path('admin/create-user/', views.admin_create_user, name='admin_create_user'),
# Add to accounts/urls.py
path('service-center/create-delivery/', views.center_create_delivery, name='center_create_delivery'),
]