

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


def staff_only(view_func):
    @login_required  # Ensures the user is logged in
    def wrapper_func(request, *args, **kwargs):
        # Check if user is in the staff group
        if request.user.groups.filter(name='staff').exists():
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the previous page or some other page
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('some_error_page')))
    
    return wrapper_func



def patient_only(view_func):
    @login_required  # Ensures the user is logged in
    def wrapper_func(request, *args, **kwargs):
        # Check if user is in the patient group
        if request.user.groups.filter(name='patient').exists():
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the previous page or some other page
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('some_error_page')))
    
    return wrapper_func

