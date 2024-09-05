from django.shortcuts import render
from . models import *
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
# Create your views here.



def index(request):
    return render(request, 'base/index.html')


def dashboard(request):
    return render(request, 'base/dashboard.html')


   # return render(request, 'patient_search.html')
def daily_logs(request):
    today = timezone.now().date()  # Get today's date

    # Filter records for today
    clinic_consultations_today = ClinicConsultation.objects.filter(date_created__date=today)
    bp_records_today = BPMonitoring.objects.filter(date_created__date=today)
    dental_cases_today = DentalCase.objects.filter(date_created__date=today)


    clinic_consultation = ClinicConsultation.objects.all()
    bp = BPMonitoring.objects.all()
    dental_case = DentalCase.objects.all()


    context = {
        'clinic_consultation': clinic_consultation,
        'BPMonitoring': bp,
        'dental_case':dental_case,

        'clinic_patients_today': clinic_consultations_today,
        'bp_patients_today': bp_records_today,
        'dental_patients_today': dental_cases_today
    }

    print(clinic_consultations_today)
    return render(request, 'base/daily_logs.html', context)



def appointments(request):
    # Get all appointments for today
    appointments = Appointment.objects.filter(date=timezone.now())

    # Filter appointments to get those with statuses 'In Queue' and 'In Progress'
    in_queue_appointments = appointments.filter(status='In Queue')
    in_progress_appointments = appointments.filter(status='In Progress')
    all_cancelled = appointments.filter(status='Cancelled').count() == appointments.count()
    
    # Determine if there are any appointments in queue or in progress
    has_in_queue_appointments = in_queue_appointments.exists()
    has_in_progress_appointments = in_progress_appointments.exists()

    context = {
        'appointments': appointments,
        'has_in_queue_appointments': has_in_queue_appointments,
        'has_in_progress_appointments': has_in_progress_appointments,
        'in_queue_appointments': in_queue_appointments,
        'in_progress_appointments': in_progress_appointments,

        'all_cancelled': all_cancelled,
    }
    return render(request, 'base/appointments.html', context)



def patients(request):
    return render(request, 'base/patients.html')


def patient_profile(request):
    return render(request, 'base/patient_profile.html')

def inventory(request):
    return render(request, 'base/inventory.html')







# FUNCTIONS 


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def patient_autocomplete(request):
    if is_ajax(request=request):
        term = request.GET.get('term', '')
        results = Patient.objects.filter(
            Q(user__username__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term)
        ).values('user__username', 'user__first_name', 'user__last_name', 'user_id_number')
                 
        suggestions = [
            {
                'name': f"{result['user__username']} - {result['user__first_name']} {result['user__last_name']}",
                'id': result['user_id_number']
            }

            for result in results
        ]

        return JsonResponse(suggestions, safe=False)
    else:
        return JsonResponse({'message': "Not a valid request"}, safe=False)
    



def add_clinic_consultation(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        chief_complaint = request.POST.get('chief_complaint')
        remarks = request.POST.get('remarks')

        patient = Patient.objects.get(user_id_number=patient_id)

        clinic_consultation = ClinicConsultation.objects.create(
            patient = patient,
            chief_complaint = chief_complaint,
            remarks = remarks
        )

        clinic_consultation.save()

        return JsonResponse({'message': 'Clinic consultation added successfully'})
    

def add_bp_monitoring(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        systolic = request.POST.get('systolic')
        diastolic = request.POST.get('diastolic')
        heart_rate = request.POST.get('heart_rate')
        remarks = request.POST.get('bp_remarks')

        patient = Patient.objects.get(user_id_number=patient_id)

        bp_monitoring = BPMonitoring.objects.create(
            patient = patient,
            systolic = systolic,
            diastolic = diastolic,
            heart_rate = heart_rate,
            remarks = remarks
        )

        bp_monitoring.save()

        return JsonResponse({'message': 'BP monitoring added successfully'})
    
def add_dental_case(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        treatment_needed = request.POST.get('treatment_needed')
        remarks = request.POST.get('dental_remarks')

        patient = Patient.objects.get(user_id_number=patient_id)

        dental_case = DentalCase.objects.create(
            patient = patient,
            treatment_needed = treatment_needed,
            remarks = remarks
        )

        dental_case.save()

        return JsonResponse({'message': 'Dental case added successfully'})
    






# Patient VIEWS


def patient_index(request):
    return render(request, 'base/patient_index.html')




def request_appointment(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        date = request.POST.get('date')
        reason = request.POST.get('reason')

        patient = Patient.objects.get(user=patient_id)

        appointment = Appointment.objects.create(
            patient = patient,
            date = date,
            reason = reason
        )

        appointment.save()

        return JsonResponse({'message': 'Appointment requested successfully'})
    

def patient_appointment_in_progress(request, appointment_id):
    
    appoinment = Appointment.objects.get(id=appointment_id)

    appoinment.status = 'In Progress'

    appoinment.save()



def send_appointment_reminders(request):


    today = timezone.now().date()

    appointments = Appointment.objects.filter(
        date=today,
        status__in=['Pending'],
    )

    for appointment in appointments:
        patient = appointment.patient
        email = patient.user.email  # Assuming email is stored in the User model

        # Craft a clear and informative email message
        subject = f"L-NU Infimary Appointment Reminder: {appointment.date}"
        message = f"""
        Dear {patient.user.first_name.capitalize()} {patient.user.last_name.capitalize()},

        This is a friendly reminder that you have an appointment scheduled for today, {appointment.date}, at L-NU Infirmary.

        We're happy to inform you that a doctor is now available to proceed with your appointment.

        **Important Information:**

        * Infirmary Hours: 9:00 AM - 4:00 PM
        * Please bring any necessary medical records or documents with you.

        If you need to reschedule your appointment, kindly contact us as soon as possible.

        We look forward to seeing you soon!

        Sincerely,

        L-NU Infirmary Staff
        """

        # Send the email
        try:
            send_mail(
                subject,
                message,
                'your_clinic_email@example.com', 
                [email],
                fail_silently=False,  
            )
        except Exception as e:
            print(f"Error sending email to {email}: {e}")
    
    return JsonResponse({'message': 'Emails sent successfully'})

def send_cancel_appointment_reminder(request):
    today = timezone.now().date()

    appointments = Appointment.objects.filter(
        date=today,
    )

    for appointment in appointments:
        patient = appointment.patient
        email = patient.user.email  # Assuming email is stored in the User model
        
        # Update appointment status to 'Cancelled'
        appointment.status = 'Cancelled'
        appointment.save()  # Save the change to the database

        # Craft a clear and informative email message
        subject = f"L-NU Infirmary Appointment Cancellation: {appointment.date}"
        message = f"""
        Dear {patient.user.first_name.capitalize()} {patient.user.last_name.capitalize()},

        We regret to inform you that your appointment scheduled for today, {appointment.date}, at L-NU Infirmary has been cancelled due to the doctor's unavailability.

        We apologize for any inconvenience this may cause. If you need to reschedule your appointment or have any questions, please contact us at your earliest convenience.

        **Contact Information:**

        * Phone: (Your Clinic Phone Number)
        * Email: your_clinic_email@example.com

        Thank you for your understanding.

        Sincerely,

        L-NU Infirmary Staff
        """

        # Send the email
        try:
            send_mail(
                subject,
                message,
                'your_clinic_email@example.com', 
                [email],
                fail_silently=False,  
            )
        except Exception as e:
            print(f"Error sending email to {email}: {e}")
    
    return JsonResponse({'message': 'Emails sent successfully'})
