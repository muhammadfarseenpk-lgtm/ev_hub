# admin_module/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from accounts.decorators import role_required
from accounts.models import User
from bookings.models import Booking
from .models import Complaint, SystemLog
from .forms import AdminRoleCreationForm

@login_required
@role_required('ADMIN')
def admin_dashboard(request):
    total_users = User.objects.exclude(role='ADMIN').count()
    pending_approvals = User.objects.filter(is_approved=False).count()
    
    # Calculate Platform Revenue (Assuming a platform fee could be extracted, here we just show total transaction volume)
    completed_bookings = Booking.objects.filter(status='COMPLETED')
    revenue_stats = completed_bookings.aggregate(Sum('total_cost'))['total_cost__sum'] or 0.00
    
    context = {
        'total_users': total_users,
        'pending_approvals': pending_approvals,
        'revenue_stats': revenue_stats,
    }
    return render(request, 'admin_module/dashboard.html', context)

@login_required
@role_required('ADMIN')
def user_management(request):
    users = User.objects.exclude(id=request.user.id).order_by('-date_joined')
    return render(request, 'admin_module/users.html', {'users': users})

@login_required
@role_required('ADMIN')
def toggle_user_status(request, user_id, action):
    target_user = get_object_or_404(User, id=user_id)
    
    if action == 'approve':
        target_user.is_approved = True
        messages.success(request, f"User {target_user.username} approved.")
    elif action == 'block':
        target_user.is_active = False
        messages.warning(request, f"User {target_user.username} has been blocked.")
    elif action == 'unblock':
        target_user.is_active = True
        messages.success(request, f"User {target_user.username} has been unblocked.")
        
    target_user.save()
    
    # Log the action
    SystemLog.objects.create(
        action=f"Admin {action}ed user ID {target_user.id} ({target_user.role})",
        performed_by=request.user
    )
    
    return redirect('admin_users')

@login_required
@role_required('ADMIN')
def role_management(request):
    if request.method == 'POST':
        form = AdminRoleCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            
            SystemLog.objects.create(
                action=f"Created new {new_user.get_role_display()}: {new_user.username}",
                performed_by=request.user
            )
            
            messages.success(request, f"Account for {new_user.username} created successfully.")
            return redirect('admin_users')
    else:
        form = AdminRoleCreationForm()
        
    return render(request, 'admin_module/create_role.html', {'form': form})

@login_required
@role_required('ADMIN')
def complaint_list(request):
    complaints = Complaint.objects.all().order_by('is_resolved', '-created_at')
    return render(request, 'admin_module/complaints.html', {'complaints': complaints})

@login_required
@role_required('ADMIN')
def resolve_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    complaint.is_resolved = True
    complaint.save()
    messages.success(request, "Complaint marked as resolved.")
    return redirect('admin_complaints')

@login_required
@role_required('ADMIN')
def activity_logs(request):
    logs = SystemLog.objects.all().order_by('-timestamp')[:100] # Show last 100
    return render(request, 'admin_module/logs.html', {'logs': logs})

# admin_module/views.py (Update the user_management view)
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
@role_required('ADMIN')
def user_management(request):
    users_list = User.objects.exclude(id=request.user.id).order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
        
    # Filter by Role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users_list = users_list.filter(role=role_filter)

    # Pagination (15 users per page)
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