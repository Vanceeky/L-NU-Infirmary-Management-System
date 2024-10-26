from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from . models import *
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.mail import send_mail

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

import random
import string
from datetime import datetime, date

from django.db import transaction
from django.contrib.auth.models import Group


# Create your views here.

# 403 Forbidden
def custom_403_view(request, exception=None):
    return render(request, 'authentication/errors/403.html', status=403)

# 404 Page Not Found
def custom_404_view(request, exception=None):
    return render(request, 'authentication/errors/404.html', status=404)

# 500 Server Error
def custom_500_view(request):
    return render(request, 'authentication/errors/500.html', status=500)



def login_page(request):
    return render(request, 'authentication/login.html')


def register_page(request):
    return render(request, 'authentication/register.html')


def staff_login_page(request):
    return render(request, 'authentication/login_staff.html')


def combined_logout(request):
    # Log out the user
    logout(request)
    
    # Optionally, add a success message
    messages.success(request, 'You have been successfully logged out.')
    
    # Redirect to the login page or home page
    return redirect('index') 


def combined_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')  # 'patient' or 'staff'

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:

            if not user.is_active:
                messages.warning(request, 'Your account is currently inactive. Please contact the administrator for approval.')
                return redirect(f'{user_type}-login-page') 
            
            if user_type == 'patient' and user.groups.filter(name='patient').exists():
                
                login(request, user)
                return redirect('index') 
            
            elif user_type == 'staff' and user.groups.filter(name='staff').exists():
                
                login(request, user)
                return redirect('dashboard')
            
            else:
                messages.error(request, 'Invalid login for the specified user type.')
                return redirect(f'{user_type}-login-page')  
        else:
            # Authentication failed
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect(f'{user_type}-login-page')  

    return redirect('index')







def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def register_user(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_id = request.POST.get('user_id')
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                email = request.POST.get('email')
                birthdate_str = request.POST.get('birthdate')
                birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                contact_number = request.POST.get('contact_number')
                gender = request.POST.get('gender')
                category = request.POST.get('category')
                designation = request.POST.get('designation')
                proof = request.FILES.get('proof')

                # Generate a secure random password with at least 8 characters
                # Check if the user_id_number or email already exists
                if Patient.objects.filter(user_id_number=user_id).exists():
                    return JsonResponse({'status': 'error', 'message': 'User ID already exists'}, status=400)
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'status': 'error', 'message': 'Email already in use'}, status=400)


                # Create the User object with hashed password
                user = User.objects.create_user(
                    username=user_id,
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    is_active=False,
                )


                patient_group, created = Group.objects.get_or_create(name='patient')
                user.groups.add(patient_group)

                # Create the Patient object
                patient = Patient.objects.create(
                    user=user,
                    user_id_number=user_id,
                    contact_number=contact_number,
                    gender=gender,
                    age=calculate_age(birthdate),
                    category=category,
                    designation=designation,
                    proof=proof,
                )

                subject = "Lyceum-Northwestern University Infirmary Account Registration"
                message = f"""
                Hi {firstname.capitalize()} {lastname.capitalize()},

                This email confirms that you have successfully registered for an account at Lyceum-Northwestern University Infirmary.

                **Please note:** Your account is currently inactive and awaits approval. You will be notified within 24 hours regarding the status of your registration.

                Thank you for choosing Lyceum!

                Sincerely,
                Lyceum-Northwestern University Infirmary Team
                """

                send_mail(
                    subject, message, 'noreply@lyceum.edu.ph', [email], fail_silently=False
                )

                message = 'You will be notified within 24 hours regarding the approval status of your registration. A confirmation email has been sent to your provided address.'

                return JsonResponse({'status': 'success', 'message': message}, status=201)

        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'User ID already exists'}, status=400)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    



def access_denied(request):
    return render(request, 'authentication/access_denied.html')