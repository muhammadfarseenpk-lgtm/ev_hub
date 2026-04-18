# core/views.py
from django.shortcuts import render, redirect

# Add this new home view
def home(request):
    return redirect('login')

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)# core/views.py
from django.shortcuts import render, redirect

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')
    return redirect('login')

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)

from django.shortcuts import render

def landing_page(request):
    return render(request, 'landing.html')