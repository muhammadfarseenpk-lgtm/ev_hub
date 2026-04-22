from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login') # Redirect to your login page name
            
            # Check if the user's role is in the list of allowed roles
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # If they don't have permission, block them
            raise PermissionDenied 
        return _wrapped_view
    return decorator