from django.shortcuts import redirect
from functools import wraps

def job_required(required_positions):
    """
    Decorator to check if a user has one of the required job positions.
    Usage: @job_required(['Manager', 'Supervisor'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.profile.job_position.name in required_positions:
                return view_func(request, *args, **kwargs)
            return redirect('no_access')  # Redirect if unauthorized
        return _wrapped_view
    return decorator
