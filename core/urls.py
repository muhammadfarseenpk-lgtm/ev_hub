# core/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views  # <-- Import the core views we made in Step 11

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # The missing root homepage path!
    path('', views.home, name='home'), 
    
    # Platform Apps
    path('', include('accounts.urls')), # Handles /login/ and /register/
    path('owner/', include('owner.urls')),
    path('station/', include('station.urls')),
    path('bookings/', include('bookings.urls')),
    path('service/', include('service.urls')),
    path('delivery/', include('delivery.urls')),
    path('platform-admin/', include('admin_module.urls')),
    path('notifications/', include('notifications.urls')),
]

# Custom Error Handlers (From Step 11)
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
handler403 = 'core.views.custom_403'