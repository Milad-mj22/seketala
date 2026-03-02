from functools import wraps
from django.shortcuts import redirect

def require_login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("logged_in"):
            return redirect("vault:simple_login")
        return view_func(request, *args, **kwargs)
    return wrapper
