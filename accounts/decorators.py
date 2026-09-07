from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def manager_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.profile.role != 'MANAGER':
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


def role_required(required_role):

    def decorator(view_func):

        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            if request.user.profile.role != required_role:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator