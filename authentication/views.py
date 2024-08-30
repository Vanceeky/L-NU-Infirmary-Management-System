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
from django.contrib.auth.hashers import make_password 
import random
import string
from datetime import datetime, date


# Create your views here.


def login_page(request):
    return render(request, 'authentication/login.html')


def register_page(request):
    return render(request, 'authentication/register.html')







def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user is active
            if not user.is_active:
                messages.warning(request, 'Your account is currently inactive. Please contact the administrator for approval.')
                return redirect('login-page')
            else:
                # Log the user in
                login(request, user)
                return redirect('dashboard')
        else:
            # Authentication failed
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login-page')

    return redirect('login-page')

def login_user(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)

    if user is not None:
      if user.is_active:
        login(request, user)
        return redirect('dashboard')
      else:
        # User found but inactive, display specific message
        messages.warning(request, 'Your account is currently inactive. Please contact the administrator for approval.')
    else:
      # User not found (or invalid credentials)
      messages.error(request, 'Invalid credentials. Please try again.')

  # Redirecting to login page in case of GET request or unsuccessful POST
  return redirect('login-page')


def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

from django.db import transaction
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
                chars = string.ascii_letters + string.digits
                random_password = ''.join(random.choice(chars) for _ in range(8))

                # Create the User object with hashed password
                user = User.objects.create_user(
                    username=user_id,
                    password=random_password,
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    is_active=False,
                )

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

                Your login credentials are:
                Username: {user_id}
                Password: {random_password}

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