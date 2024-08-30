from django.shortcuts import render
from . models import *
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q

# Create your views here.



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
    return render(request, 'base/appointments.html')

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