# admin_module/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator

from accounts.decorators import role_required
from accounts.models import User
from .models import SupportTicket, SystemLog
from .forms import AdminRoleCreationForm

@login_required
@role_required('ADMIN')
def admin_dashboard(request):
    total_users = User.objects.exclude(role='ADMIN').count()
    owners_count = User.objects.filter(role='EV_OWNER').count()
    operators_count = User.objects.filter(role='STATION_OPERATOR').count()
    services_count = User.objects.filter(role='SERVICE_CENTER').count()
    open_tickets = SupportTicket.objects.filter(status='OPEN').count()
    
    context = {
        'total_users': total_users,
        'owners_count': owners_count,
        'operators_count': operators_count,
        'services_count': services_count,
        'open_tickets': open_tickets,
        # Note: Revenue logic can be linked here later if you import the Booking model!
        'revenue_stats': 0.00, 
    }
    return render(request, 'admin_module/dashboard.html', context)

@login_required
@role_required('ADMIN')
def user_management(request):
    users_list = User.objects.exclude(id=request.user.id).order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
        
    # Role filter functionality
    role_filter = request.GET.get('role', '')
    if role_filter:
        users_list = users_list.filter(role=role_filter)

    # Pagination
    paginator = Paginator(users_list, 15)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': User.RoleChoices.choices,
    }
    return render(request, 'admin_module/users.html', context)

@login_required
@role_required('ADMIN')
def toggle_user_status(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    status = "unblocked" if target_user.is_active else "blocked"
    
    # Log the action
    SystemLog.objects.create(
        action=f"Admin {status} user ID {target_user.id} ({target_user.username})",
        user=request.user
    )
    
    messages.success(request, f"User '{target_user.username}' has been successfully {status}.")
    return redirect('user_management')

@login_required
@role_required('ADMIN')
def role_management(request):
    if request.method == 'POST':
        form = AdminRoleCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            SystemLog.objects.create(
                action=f"Created new {new_user.get_role_display()}: {new_user.username}",
                user=request.user
            )
            messages.success(request, f"Account for {new_user.username} created successfully.")
            return redirect('user_management')
    else:
        form = AdminRoleCreationForm()
    return render(request, 'admin_module/create_role.html', {'form': form})

@login_required
@role_required('ADMIN')
def complaint_list(request):
    # Changed Complaint to SupportTicket to match your models.py
    complaints = SupportTicket.objects.all().order_by('status', '-created_at')
    return render(request, 'admin_module/complaints.html', {'complaints': complaints})

@login_required
@role_required('ADMIN')
def resolve_complaint(request, pk):
    complaint = get_object_or_404(SupportTicket, pk=pk)
    complaint.status = 'RESOLVED'
    complaint.save()
    messages.success(request, "Ticket marked as resolved.")
    return redirect('admin_complaints')

@login_required
@role_required('ADMIN')
def activity_logs(request):
    logs = SystemLog.objects.all().order_by('-timestamp')[:100]
    return render(request, 'admin_module/logs.html', {'logs': logs})