from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name="index"),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('daily-logs/', views.daily_logs, name="daily-logs"),
    
    path('patients/', views.patients, name="patients"),
    path('patient-profile/<str:patient_id>/', views.view_patient_dashboard, name="patient-profile-dashboard"),
    path('patient/<int:patient_id>/', views.patient_profile, name="patient-profile"),


    path('inventory/', views.inventory, name="inventory"),
    path('appointments/', views.appointments, name="appointments"),

    path('update-appointment-status/<int:appointment_id>/', views.update_appointment_status, name='update-appointment-status'),
    path('fetch-appointments/', views.fetch_appointments, name='fetch-appointments'),


    path('search_patient/', views.patient_autocomplete, name="search-patient"),

    path('add-clinic-consultation-log/', views.add_clinic_consultation, name="add-clinic-consultation"),

    path('add-dental-case-log/', views.add_dental_case, name="add-dental-case"),

    path('add-bp-monitoring-log/', views.add_bp_monitoring, name="add-bp-monitoring"),

    path('add-vaccination-log/', views.add_vaccination, name="add-vaccination"),

    path('request-appointment/', views.request_appointment, name="request-appointment"),
    path('appointment-reminder/', views.send_appointment_reminders, name="appointment-reminder"),
    path('appointment-reminder/cancelled/', views.send_cancel_appointment_reminder, name="cancel-appointment-reminder"),

    path('medical-certificates/', views.medcerts, name="medcerts"),


    path('request-med-cert/', views.request_medcert, name="request-medcert"),
    path('med-cert/requests/', views.medical_certificate_requests, name="med-cert-requests"),
    path('approve-med-cert/', views.approve_med_cert_request, name='approve-med-cert'),
    path('view-med-cert/<int:certificate_id>/', views.view_medical_certificate, name='view-med-cert'),


    path('api/monthly-model-counts/', views.monthly_model_counts, name='monthly_model_counts'),
    path('api/model-counts/', views.model_counts, name='model_counts'),


]
