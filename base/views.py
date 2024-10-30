from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseForbidden, HttpResponse
from . models import *
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
# Create your views here.
import calendar
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import ExtractMonth
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from io import BytesIO
import qrcode


from django.core.files.base import ContentFile

from .decorators import staff_only, patient_only

from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string
from django.urls import reverse
from twilio.rest import Client

# Twilio configuration
account_sid = 'ACc7dad14ba8cb5c1a9ab6f690839935da'
auth_token = 'f238954cc6bf25a59bb58523413df7d0'
client = Client(account_sid, auth_token)


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
        else:
            # If the user is authenticated but not a patient, redirect to an error page

            raise PermissionDenied

    # Render the page for authenticated patients or unauthenticated users
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

        purpose = request.POST.get('purpose')
        reason = request.POST.get('reason')


        additional_notes = request.POST.get('additional_notes')
        additional_file = request.FILES.get('supporting_document')


        MedicalCertificateRequest.objects.create(
            patient = patient,
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
    vaccination_records_today = Vaccination.objects.filter(date_created__date=today)


    clinic_consultation = ClinicConsultation.objects.all()
    bp = BPMonitoring.objects.all()
    dental_case = DentalCase.objects.all()
    vaccination = Vaccination.objects.all()


    patients = Patient.objects.all()

    context = {
        'clinic_consultation': clinic_consultation,
        'BPMonitoring': bp,
        'dental_case':dental_case,
        'vaccination':vaccination,

        'clinic_patients_today': clinic_consultations_today,
        'bp_patients_today': bp_records_today,
        'dental_patients_today': dental_cases_today,
        'vaccination_patients_today': vaccination_records_today,

        'patients': patients
    }

    print(clinic_consultations_today)
    return render(request, 'base/daily_logs.html', context)


def appointments(request):
    # Get all appointments for today
    today = timezone.now().date()
    appointments = AppointmentRequest.objects.filter(date=today)

    # Check if there are any appointments
    no_appointments_today = not appointments.exists()

    if not no_appointments_today:
        # Filter appointments to get those with statuses 'In Queue' and 'In Progress'
        in_queue_appointments = appointments.filter(status='In Queue')
        in_progress_appointments = appointments.filter(status='In Progress')
        all_cancelled = appointments.filter(status='Cancelled').count() == appointments.count()

        context = {
            'appointments': appointments,
            'has_in_queue_appointments': in_queue_appointments.exists(),
            'has_in_progress_appointments': in_progress_appointments.exists(),
            'in_queue_appointments': in_queue_appointments,
            'in_progress_appointments': in_progress_appointments,
            'all_cancelled': all_cancelled,
        }
    else:
        context = {
            'all_cancelled': False,  # No appointments means this flag is irrelevant
            'no_appointments_today': True
        }

    return render(request, 'base/appointments.html', context)


def update_appointment_status(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(AppointmentRequest, id=appointment_id)

        # Check if there are any patients currently in progress
        in_progress_appointments = AppointmentRequest.objects.filter(status='In Progress', date=timezone.now().date())

        if in_progress_appointments.exists():
            # If there's a patient in progress, set the current appointment to 'In Queue'
            appointment.status = 'In Queue'
        else:
            # If there's no patient in progress, set the current appointment to 'In Progress'
            appointment.status = 'In Progress'

        appointment.save()

        return JsonResponse({'status': 'success', 'new_status': appointment.status})

    return JsonResponse({'status': 'error'}, status=400)


def fetch_appointments(request):
    today = timezone.now().date()
    in_progress_appointments = AppointmentRequest.objects.filter(date=today, status='In Progress')
    in_queue_appointments = AppointmentRequest.objects.filter(date=today, status='In Queue')

    # Prepare data for JSON response
    in_progress_data = [
        {
            'id': ap.id,
            'patient_id': ap.patient.id,

            'first_name': ap.patient.user.first_name,
            'last_name': ap.patient.user.last_name,
            'category': ap.patient.category,
            'designation': ap.patient.designation
        }
        for ap in in_progress_appointments
    ]

    in_queue_data = [
        {
            'id': ap.id,
            'first_name': ap.patient.user.first_name,
            'last_name': ap.patient.user.last_name,
            'category': ap.patient.category,
            'designation': ap.patient.designation
        }
        for ap in in_queue_appointments
    ]

    return JsonResponse({
        'in_progress': in_progress_data,
        'in_queue': in_queue_data
    })



def appointment_remarks(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        appointment_id = request.POST.get('appointment_id')
        remarks = request.POST.get('remarks')

        request_ = AppointmentRequest.objects.get(id=appointment_id)

        patient = Patient.objects.get(id=patient_id)

        request_.status = 'Completed'
        request_.save()

        appointment = Appointment.objects.create(
            patient = patient,
            purpose = request_.reason,
            remarks = remarks,
        )

        appointment.save()

        return JsonResponse({'message': 'Appointment remarks updated successfully'})



def move_first_in_queue(request):
    if request.method == 'POST':
        first_in_queue = AppointmentRequest.objects.filter(status='In Queue').order_by('date_created').first()
        if first_in_queue:
            first_in_queue.status = 'In Progress'
            first_in_queue.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'no_appointments'})
        

def patients(request):

    

    clinic_visits = ClinicConsultation.objects.filter(patient=OuterRef('pk')).annotate(
        visit_date=Subquery(ClinicConsultation.objects.filter(patient=OuterRef('pk')).values('date_created'))
    ).values('visit_date')

    bp_visits = BPMonitoring.objects.filter(patient=OuterRef('pk')).annotate(
        visit_date=Subquery(BPMonitoring.objects.filter(patient=OuterRef('pk')).values('date_created'))
    ).values('visit_date')

    dental_visits = DentalCase.objects.filter(patient=OuterRef('pk')).annotate(
        visit_date=Subquery(DentalCase.objects.filter(patient=OuterRef('pk')).values('date_created'))
    ).values('visit_date')

    appointment_visits = Appointment.objects.filter(patient=OuterRef('pk')).annotate(
        visit_date=Subquery(Appointment.objects.filter(patient=OuterRef('pk')).values('date_created'))
    ).values('visit_date')

    medical_certificates = MedicalCertificate.objects.filter(patient=OuterRef('pk')).annotate(
        visit_date=Subquery(MedicalCertificate.objects.filter(patient=OuterRef('pk')).values('date_created'))
    ).values('visit_date')

    recent_visit_date = Subquery(
        clinic_visits.union(bp_visits).union(dental_visits).union(appointment_visits).union(medical_certificates)
        .order_by('-visit_date')[:1]
    )
    
    patient_group = Group.objects.get(name='patient')
    inactive_users = User.objects.filter(groups=patient_group, is_active=False)

    patients = Patient.objects.annotate(
        visit_count=Count('clinicconsultation') + Count('bpmonitoring') + Count('dentalcase') +
                    Count('appointment') + Count('medicalcertificate'),
        recent_visit_date=recent_visit_date
    ).exclude(user__in=inactive_users)

    



    inactive_patients = Patient.objects.filter(user__in=inactive_users)

    patient_student_count = patients.filter(category = 'Student').count()
    patient_employee_count = patients.filter(category = 'Employee').count()

    context = {
        'patients': patients,
        'patient_student_count': patient_student_count,
        'patient_employee_count': patient_employee_count,
        'inactive_patients': inactive_patients
    }
    
    return render(request, 'base/patients.html', context)



def patient_account_request(request):
    return render(request, 'base/patient_account_request.html')


def medcerts(request):
    patients = Patient.objects.all()
    medcert_requests = MedicalCertificateRequest.objects.all().order_by('-date_created')
    medcerts = MedicalCertificate.objects.all().order_by('-date_created')

    context = {
        'patients': patients,
        'medcerts': medcerts,
        'medcert_requests': medcert_requests
    }
    return render(request, 'base/medcerts.html', context)

def receive_med_cert(request, medcert_id):
    medcert = get_object_or_404(MedicalCertificate, id=medcert_id)
    medcert.mark_as_received()
    return redirect('medcerts')


def medical_certificate_requests(request):
    if request.method == 'GET':
        requests = MedicalCertificateRequest.objects.all().order_by('-date_created')
        data = [
            {
                'id': req.id,
                'patient': req.patient.id,
                'purpose': req.purpose,
                'reason': req.reason,
                'additional_notes': req.additional_notes,
                'additional_file': req.additional_file.url if req.additional_file else None,
                'status': req.status,
                'date_created': req.date_created.isoformat(),
            }
            for req in requests
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def create_medcert(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        purpose = request.POST.get('purpose')
        remarks = request.POST.get('remarks')

        patient = get_object_or_404(Patient, id=patient_id)

        medical_certificate = MedicalCertificate.objects.create(
            request_id=None,
            patient=patient,
            purpose=purpose,
            remarks=remarks,
            status='Issued'
        )
        
        qr_content = (
            f"Medical Certificate\n"
            f"Patient Name: {medical_certificate.patient.user.get_full_name()}\n"
            f"Patient ID: {medical_certificate.patient.user_id_number}\n"
            f"Purpose: {medical_certificate.purpose}\n"
            f"Issue Date: {medical_certificate.date_created.strftime('%Y-%m-%d')}\n"
            f"Certificate ID: {medical_certificate.id}\n"
        )
        # Create QR code
        qr_image = qrcode.make(qr_content)

        # Save QR code image to BytesIO
        qr_image_io = BytesIO()
        qr_image.save(qr_image_io, format='PNG')
        qr_image_io.seek(0)  # Reset cursor to the start

        # Save QR code to the model
        qr_file_name = f'qr_codes/med_cert_{medical_certificate.id}.png'
        medical_certificate.qr_code.save(qr_file_name, ContentFile(qr_image_io.getvalue()))

        medical_certificate.save()

        return JsonResponse({'message': 'Medical certificate created successfully'})


def approve_med_cert_request(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        patient_id = request.POST.get('patient_id')
        remarks = request.POST.get('remarks')

        # Get the medical certificate request
        med_cert_request = get_object_or_404(MedicalCertificateRequest, id=request_id)

        # Update the request status to Approved
        med_cert_request.status = 'Approved'
        med_cert_request.save()

        # Create a new MedicalCertificate
        medical_certificate = MedicalCertificate(
            request_id=med_cert_request,
            patient=med_cert_request.patient,
            purpose=med_cert_request.purpose,
            remarks=remarks,
            status='Issued'
        )
        medical_certificate.save()

        # Generate QR code content
        qr_content = (
            f"Medical Certificate\n"
            f"Patient Name: {medical_certificate.patient.user.get_full_name()}\n"
            f"Patient ID: {medical_certificate.patient.user_id_number}\n"
            f"Purpose: {medical_certificate.purpose}\n"
            f"Issue Date: {medical_certificate.date_created.strftime('%Y-%m-%d')}\n"
            f"Certificate ID: {medical_certificate.id}\n"
        )
        # Create QR code
        qr_image = qrcode.make(qr_content)

        # Save QR code image to BytesIO
        qr_image_io = BytesIO()
        qr_image.save(qr_image_io, format='PNG')
        qr_image_io.seek(0)  # Reset cursor to the start

        # Save QR code to the model
        qr_file_name = f'qr_codes/med_cert_{medical_certificate.id}.png'
        medical_certificate.qr_code.save(qr_file_name, ContentFile(qr_image_io.getvalue()))

        # Save the medical certificate with QR code
        medical_certificate.save()

        messages.success(request, 'Medical certificate request approved successfully.')
        return redirect('view-med-cert', medical_certificate.id)  # Replace with your desired URL

    return HttpResponse(status=400)


def view_medical_certificate(request, certificate_id):
    certificate = get_object_or_404(MedicalCertificate, id=certificate_id)
    return render(request, 'base/staff/med-cert-file.html', {'cert': certificate})

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
    

def add_vaccination(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        vaccine_name = request.POST.get('vaccine_name')
        dose = request.POST.get('dose')

        next_dose_due = request.POST.get('next_dose_due')
        if next_dose_due == '':
            next_dose_due = '';

        patient = Patient.objects.get(user_id_number=patient_id)

        vaccination = Vaccination.objects.create(
            patient = patient,
            vaccine_name = vaccine_name,
            dose = dose,
            next_dose_due = next_dose_due
        )

        vaccination.save()

        return JsonResponse({'message': 'Vaccination added successfully'})




# Patient VIEWS

def view_patient_dashboard(request, patient_id):

    patient = Patient.objects.get(user_id_number=patient_id)

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

    return render(request, 'base/patient_profile.html', context)


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
            'certificate': reverse('view-med-cert', args=[certificate.id]) 
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

        patient = get_object_or_404(Patient, user=patient_id)

        # Check for existing request
        existing_request = AppointmentRequest.objects.filter(patient=patient, date=date).first()
        if existing_request:
            return JsonResponse({'message': 'You have already requested an appointment for this date.'}, status=400)

        # Create new request if no existing request is found
        appointment = AppointmentRequest.objects.create(
            patient=patient,
            date=date,
            reason=reason
        )

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
        patient = appointment.status = 'Notified'

        appointment.save()

        patient = appointment.patient
        email = patient.user.email
        phone_number = patient.contact_number  # Ensure this field exists for storing patient phone numbers

        # Email message
        subject = f"L-NU Infirmary Appointment Reminder: {appointment.date}"
        message = f"""
        Dear {patient.user.first_name.capitalize()} {patient.user.last_name.capitalize()},

        This is a friendly reminder that you have an appointment scheduled for today, {appointment.date}, at L-NU Infirmary.

        A doctor is now available to proceed with your appointment.

        **Important Information:**
        * Infirmary Hours: 9:00 AM - 4:00 PM
        * Please bring any necessary medical records or documents with you.

        We look forward to seeing you soon!
        
        Sincerely,
        L-NU Infirmary Staff
        """

        # Send email
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

        # Send SMS
        try:
            sms_message = client.messages.create(
                from_='+14014913327',
                
                body=f"Appointment Today LNU",
                to='+639776288749'
            )
            print(f"SMS sent to {phone_number}, SID: {sms_message.sid}")
        except Exception as e:
            print(f"Error sending SMS to {phone_number}: {e}")

    return JsonResponse({'message': 'Reminders sent successfully'})

def send_cancel_appointment_reminder(request):
    today = timezone.now().date()

    appointments = AppointmentRequest.objects.filter(
        date=today,
    )

    for appointment in appointments:
        patient = appointment.patient
        email = patient.user.email
        phone_number = patient.contact_number

        # Update appointment status to 'Cancelled'
        appointment.status = 'Cancelled'
        appointment.save()

        # Email message
        subject = f"L-NU Infirmary Appointment Cancellation: {appointment.date}"
        message = f"""
        Dear {patient.user.first_name.capitalize()} {patient.user.last_name.capitalize()},

        We regret to inform you that your appointment scheduled for today, {appointment.date}, at L-NU Infirmary has been cancelled due to the doctor's unavailability.

        Thank you for your understanding.

        Sincerely,
        L-NU Infirmary Staff
        """

        # Send email
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

        # Send SMS
        try:
            sms_message = client.messages.create(
                body=f"Appointment Cancelled",
                from_='+14014913327',
                to=phone_number
            )
            print(f"Cancellation SMS sent to {phone_number}, SID: {sms_message.sid}")
        except Exception as e:
            print(f"Error sending SMS to {phone_number}: {e}")

    return JsonResponse({'message': 'Cancellations sent successfully'})






def medicine_supply(request):
    medicines = Medicine.objects.all()
    patients = Patient.objects.all()
    medicines_usages = MedicineUsage.objects.all()

    context = {
        'medicines': medicines,
        'patients': patients,
        'medicines_usages': medicines_usages,

    }
    return render(request, 'base/medicine_supply.html', context)



# View for adding medicine
def add_medicine(request):
    if request.method == 'POST':
        name = request.POST['name']
        quantity_in_stock = request.POST['quantity_in_stock']
        unit_of_measure = request.POST['unit_of_measure']
        expiration_date = request.POST['expiration_date']
        description = request.POST['description']

        # Case-insensitive check if the medicine with the same name already exists
        if Medicine.objects.filter(name__iexact=name).exists():
            response = {
                'status': 'error',
                'message': f"{name} already exists in the inventory."
            }
            return JsonResponse(response, status=400)

        try:
            # Create the new medicine entry
            medicine = Medicine.objects.create(
                name=name,
                quantity_in_stock=quantity_in_stock,
                unit_of_measure=unit_of_measure,
                expiration_date=expiration_date,
                description=description,
            )

            response = {
                'status': 'success',
                'message': f"{medicine.name} has been added to the inventory."
            }
            return JsonResponse(response)

        except Exception as e:
            # Error handling
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def add_medication(request):
    if request.method == "POST":
        try:
            # Get the data from the request
            patient_id = request.POST.get('patient')
            medicine_id = request.POST.get('medicine')
            quantity_used = int(request.POST.get('quantity'))
            remarks = request.POST.get('remarks')

            # Fetch the patient and medicine objects
            medicine = Medicine.objects.get(id=medicine_id)
            patient = Patient.objects.get(id=patient_id)

            # Check if the quantity is available
            if quantity_used > medicine.quantity_in_stock:
                return JsonResponse({'status': 'error', 'message': 'Not enough stock available.'}, status=400)

            # Create the MedicineUsage record
            medicine_usage = MedicineUsage(
                patient=patient,
                medicine=medicine,
                quantity_used=quantity_used,
                remarks=remarks
            )
            medicine_usage.save()

            # Return a success response with status
            return JsonResponse({'status': 'success', 'message': 'Medication added successfully.'}, status=201)

        except Medicine.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Medicine not found.'}, status=404)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



# View for updating medicine supply
def update_medicine_supply(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        quantity_added = int(request.POST['quantity_added'])
        remarks = request.POST.get('remarks', '')

        restock = MedicineRestock.objects.create(
            medicine=medicine,
            quantity_added=quantity_added,
            remarks=remarks
        )
        response = {
            'status': 'success',
            'message': f"{quantity_added} units of {medicine.name} were added to the inventory."
        }
        return JsonResponse(response)
    
    return render(request, 'base/medicine_supply.html', {'medicine': medicine})

# View for adding medicine usage
def add_medicine_usage(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    medicines = Medicine.objects.all()

    if request.method == 'POST':
        medicine_id = request.POST['medicine']
        quantity_used = int(request.POST['quantity_used'])
        remarks = request.POST.get('remarks', '')

        medicine = get_object_or_404(Medicine, id=medicine_id)
        if medicine.quantity_in_stock >= quantity_used:

            usage = MedicineUsage.objects.create(
                patient=patient,
                medicine=medicine,
                quantity_used=quantity_used,
                remarks=remarks
            )
            response = {
                'status': 'success',
                'message': f"{quantity_used} units of {medicine.name} have been given to {patient.user.first_name}."
            }
        else:
            response = {
                'status': 'error',
                'message': f"Not enough {medicine.name} in stock."
            }
        return JsonResponse(response)
    
    return render(request, 'base/medicine_supply.html', {'patient': patient, 'medicines': medicines})



def approve_user_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Generate a new password
    raw_password = get_random_string(length=8)  # You can customize the password length

    # Set the password for the user
    user.set_password(raw_password)
    user.is_active = True
    user.save()

    # Send approval email notification with the raw password
    subject = "Your Lyceum-Northwestern University Infirmary Account is Approved"
    message = f"""
    Hi {user.first_name.capitalize()} {user.last_name.capitalize()},

    We are pleased to inform you that your account at Lyceum-Northwestern University Infirmary has been approved.
    
    You can now log in to your account using the following details:
    Username: {user.username}
    Password: {raw_password}

    Thank you for choosing Lyceum-Northwestern University Infirmary.

    Sincerely,
    Lyceum-Northwestern University Infirmary Team
    """
    send_mail(
        subject, message, 'noreply@lyceum.edu.ph', [user.email], fail_silently=False
    )

    return redirect('patients')

def reject_user_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Send rejection email notification
    subject = "Your Lyceum-Northwestern University Infirmary Account Registration"
    message = f"""
    Hi {user.first_name.capitalize()} {user.last_name.capitalize()},

    We regret to inform you that your account registration at Lyceum-Northwestern University Infirmary has been rejected.
    
    If you believe this is an error or if you have any questions, please contact us at support@lyceum.edu.ph.

    Thank you for your understanding.

    Sincerely,
    Lyceum-Northwestern University Infirmary Team
    """
    send_mail(
        subject, message, 'noreply@lyceum.edu.ph', [user.email], fail_silently=False
    )

    # Delete the user after sending the rejection email
    user.delete()

    return redirect('patients')



def update_patient_information(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        category = request.POST.get('category')
        designation = request.POST.get('designation')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        avatar = request.FILES.get('avatar')

        patient = get_object_or_404(Patient, id=patient_id)

        # Check if the inputted email is the same as the existing email
        if email != patient.user.email:
            # Here you can perform a check to ensure the email is unique
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already in use by another account.'}, status=400)

        try:
            patient.category = category
            patient.designation = designation
            patient.contact_number = contact_number
            patient.address = address
            patient.user.email = email
            
            if avatar:
                patient.avatar = avatar
            
            patient.save()
            patient.user.save()  
            print(patient.user.email)
            return JsonResponse({'status': 'success', 'message': 'Patient information updated successfully.'})

        except IntegrityError as e:
            print(f"IntegrityError: {e}")  # Log the detailed error message
            return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the patient information due to database constraints.'}, status=400)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': e.message}, status=400)
        except Exception as e:
            # Log the actual error for debugging (optional)
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred while updating the patient information.'}, status=500)
        



