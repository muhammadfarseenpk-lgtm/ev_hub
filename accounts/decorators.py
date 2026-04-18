# accounts/decorators.py
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(*allowed_roles):
    """Decorator to enforce strict RBAC on views."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this module.")
        return _wrapped_view
    return decorator

