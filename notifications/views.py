from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Notification

@login_required
def notification_list(request):
    # Fetch all notifications, ordered by newest first (assuming you have ordering set in models.py)
    notif_list = request.user.notifications.all().order_by('-created_at')
    
    # Pagination: Show 15 notifications per page
    paginator = Paginator(notif_list, 15) 
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))

@login_required
def mark_all_read(request):
    unread_notifications = request.user.notifications.filter(is_read=False)
    if unread_notifications.exists():
        unread_notifications.update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect('notification_list')