# core/urls.py
from django.urls import path, include
from django.contrib import admin
from . import views
from accounts import views as account_views  # This fixes the NameError

urlpatterns = [
    # Main Homepage
    path('', views.landing_page, name='landing'),
    path('admin/', admin.site.urls),
    
    # Auth Routes
    path('login/', account_views.login_view, name='login'), 
    path('register/', account_views.register_view, name='register'),
    
    # Platform Apps
    path('accounts/', include('accounts.urls')), 
    path('owner/', include('owner.urls')),
    path('station/', include('station.urls')),
    path('bookings/', include('bookings.urls')),
    path('service/', include('service.urls')),
    path('delivery/', include('delivery.urls')),
    path('platform-admin/', include('admin_module.urls')),
    path('notifications/', include('notifications.urls')),
    path('about/', views.about_view, name='about'),
path('contact/', views.contact_view, name='contact'),
]

# Custom Error Handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
handler403 = 'core.views.custom_403'