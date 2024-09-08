from django.shortcuts import render, get_object_or_404
from django.http import Http404
from . models import *
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
# Create your views here.
import calendar
from django.db.models import Count
from django.db.models.functions import ExtractMonth

def monthly_model_counts(request):
    # Define a function to get counts per month for a given model
    def get_monthly_counts(model):
        return (
            model.objects
            .annotate(month=ExtractMonth('date_created'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

    # Get counts for each model
    medical_certificates = get_monthly_counts(MedicalCertificate)
    appointments = get_monthly_counts(Appointment)
    clinic_consultations = get_monthly_counts(ClinicConsultation)
    bp_monitorings = get_monthly_counts(BPMonitoring)
    dental_cases = get_monthly_counts(DentalCase)

    # Prepare data for the chart
    months = [calendar.month_name[i] for i in range(1, 13)]
    
    def fill_counts(counts):
        return [0] * 12

    def update_counts(counts, data):
        for entry in data:
            month = entry['month'] - 1
            counts[month] = entry['count']

    data = {
        'months': months,
        'medical_certificates': fill_counts([0] * 12),
        'appointments': fill_counts([0] * 12),
        'clinic_consultations': fill_counts([0] * 12),
        'bp_monitorings': fill_counts([0] * 12),
        'dental_cases': fill_counts([0] * 12)
    }

    update_counts(data['medical_certificates'], medical_certificates)
    update_counts(data['appointments'], appointments)
    update_counts(data['clinic_consultations'], clinic_consultations)
    update_counts(data['bp_monitorings'], bp_monitorings)
    update_counts(data['dental_cases'], dental_cases)

    return JsonResponse(data)

def model_counts(request):
    counts = {
        'Medical Certificates': MedicalCertificate.objects.count(),
        'Appointments': Appointment.objects.count(),
        'Clinic Consultations': ClinicConsultation.objects.count(),
        'BP Monitoring': BPMonitoring.objects.count(),
        'Dental Cases': DentalCase.objects.count(),
    }
    return JsonResponse(counts)

def index(request):
    # Initialize patient and records variables
    patient = None
    records = None

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Attempt to get the patient record for the logged-in user
        patient = Patient.objects.filter(user=request.user).first()

        if patient:
            # Get the patient records if the patient exists
            records = get_patient_records(patient.id)

    context = {
        'patient': patient,
        'records': records
    }
    return render(request, 'base/index.html', context)


def get_patient_records(patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    records = []

    # Fetch and format Clinic Consultations
    consultations = ClinicConsultation.objects.filter(patient=patient).order_by('-date_created')
    for consultation in consultations:
        records.append(f"{consultation.date_created.strftime('%B %d, %Y')}: Clinic Consultation")

    # Fetch and format BP Monitoring
    bp_monitorings = BPMonitoring.objects.filter(patient=patient).order_by('-date_created')
    for bp in bp_monitorings:
        records.append(f"{bp.date_created.strftime('%B %d, %Y')}: BP Monitoring")

    # Fetch and format Dental Cases
    dental_cases = DentalCase.objects.filter(patient=patient).order_by('-date_created')
    for case in dental_cases:
        records.append(f"{case.date_created.strftime('%B %d, %Y')}: Dental Case")

    return records


def request_medcert(request):

    patient = get_object_or_404(Patient, user=request.user)
    if request.method == 'POST':

        patient_record = request.POST.get('patient_record')
        purpose = request.POST.get('purpose')
        reason = request.POST.get('reason')


        additional_notes = request.POST.get('additional_notes')
        additional_file = request.FILES.get('supporting_document')


        MedicalCertificateRequest.objects.create(
            patient = patient,
            patient_record = patient_record,
            purpose = purpose,
            reason = reason,
            additional_notes = additional_notes,
            additional_file = additional_file
        )

        return JsonResponse({'message': 'Request submitted successfully'})




def dashboard(request):
    patients = Patient.objects.all()
    appointment_requests = AppointmentRequest.objects.all()
    medicial_certificate_requests = MedicalCertificateRequest.objects.all()

    students = patients.filter(category = 'Student')
    employees = patients.filter(category = 'Employee')

    appointment_completed = appointment_requests.filter(status = 'Completed')
    appointment_pending = appointment_requests.filter(status = 'Pending')

    med_cert_pending = medicial_certificate_requests.filter(status = 'Pending')
    med_cert_issued = medicial_certificate_requests.filter(status = 'Issued')


    context = {
        'students': students,
        'employees': employees,

        'appointment_completed': appointment_completed,
        'appointment_pending': appointment_pending,

        'med_cert_pending': med_cert_pending,
        'med_cert_issued': med_cert_issued
    }
    return render(request, 'base/dashboard.html', context)


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
    appointments = AppointmentRequest.objects.filter(date=timezone.now())

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



def inventory(request):
    return render(request, 'base/inventory.html')



def medcerts(request):
    medcerts = MedicalCertificateRequest.objects.all()
    context = {
        'medcerts': medcerts
    }
    return render(request, 'base/medcerts.html', context)




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

def view_patient_dashboard(request):
    return render(request, 'base/patient_profile.html')

def patient_index(request):
    return render(request, 'base/patient_index.html')


def patient_profile(request, patient_id):
    try:
        # Fetch the patient object for the logged-in user
        patient = Patient.objects.get(id=patient_id, user=request.user)
    except Patient.DoesNotExist:
        raise Http404("Patient not found")

    clinic_consultation = ClinicConsultation.objects.filter(patient=patient).order_by('-date_created')
    bp_monitoring = BPMonitoring.objects.filter(patient=patient).order_by('-date_created')
    dental_case = DentalCase.objects.filter(patient=patient).order_by('-date_created')

    certificate_requests = MedicalCertificateRequest.objects.filter(patient=patient).order_by('-date_created')
    certificates = MedicalCertificate.objects.filter(patient=patient).order_by('-date_created')
    appointment_requests = AppointmentRequest.objects.filter(patient=patient).order_by('-date_created')

    combined_records = []

    for consultation in clinic_consultation:
        combined_records.append({
            'type': 'Clinic Consultation',
            'date': consultation.date_created,
            'details': consultation.chief_complaint,
            'remarks': consultation.remarks
        })

    for bp in bp_monitoring:
        combined_records.append({
            'type': 'BP Monitoring',
            'date': bp.date_created,
            'details': f"Systolic / Diastolic: {bp.systolic} / {bp.diastolic}, Heart Rate: {bp.heart_rate}",
            'remarks': bp.remarks
        })

    for case_ in dental_case:
        combined_records.append({
            'type': 'Dental Case',
            'date': case_.date_created,
            'details': f"Treatment Needed: {case_.treatment_needed}",
            'remarks': case_.remarks
        })

    for request_ in certificate_requests:

        combined_records.append({
            'type': 'Medical Certificate Request',
            'date': request_.date_created,
            'details': f"Purpose: {request_.purpose}, Reason: {request_.reason}",
            'remarks': request_.status
        })

    for certificate in certificates:
        combined_records.append({
            'type': 'Medical Certificate',
            'date': certificate.date_created,
            'details': f"Purpose: {certificate.purpose}",
            'remarks': certificate.status,
        })

    for request_ in appointment_requests:
        combined_records.append({
            'type': 'Appointment Request',
            'date': request_.date_created,
            'details': f"Date requested: {request_.date}, Reason: {request_.reason}",
            'remarks': request_.status
        })



    # Sort the combined records by date
    combined_records.sort(key=lambda x: x['date'], reverse=True)

    context = {
        'patient': patient,
        'combined_records': combined_records
    }

    return render(request, 'base/patient/profile.html', context)


def request_appointment(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        date = request.POST.get('date')
        reason = request.POST.get('reason')

        patient = Patient.objects.get(user=patient_id)

        appointment = AppointmentRequest.objects.create(
            patient = patient,
            date = date,
            reason = reason
        )

        appointment.save()

        return JsonResponse({'message': 'Appointment requested successfully'})
    

def patient_appointment_in_progress(request, appointment_id):
    
    appoinment = AppointmentRequest.objects.get(id=appointment_id)

    appoinment.status = 'In Progress'

    appoinment.save()



def send_appointment_reminders(request):


    today = timezone.now().date()

    appointments = AppointmentRequest.objects.filter(
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

    appointments = AppointmentRequest.objects.filter(
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
