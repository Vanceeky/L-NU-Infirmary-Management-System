from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('', views.index, name="index"),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('daily-logs/', views.daily_logs, name="daily-logs"),
    
    path('patients/', views.patients, name="patients"),
    path('patient-profile/<str:patient_id>/', views.view_patient_dashboard, name="patient-profile-dashboard"),
    path('patient/<int:patient_id>/', views.patient_profile, name="patient-profile"),
    path('patient/edit/', views.update_patient_information, name="update-patient-information"),



    path('medicine-supply/', views.medicine_supply, name="medicine_supply"),
    path('add-medicine/', views.add_medicine, name="add_medicine"),
    path('add-medication/', views.add_medication, name='add_medication'),






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
    path('appointment-remarks/', views.appointment_remarks, name="appointment_remarks"),

    path('move-in-queue/', views.move_first_in_queue, name="move-first-in-queue"),

    path('medical-certificates/', views.medcerts, name="medcerts"),
    path('create-med-cert/', views.create_medcert, name="create-med-cert"),
    path('update-med-cert/<int:medcert_id>/', views.receive_med_cert, name="receive_med_cert"),


    path('request-med-cert/', views.request_medcert, name="request-medcert"),
    path('med-cert/requests/', views.medical_certificate_requests, name="med-cert-requests"),
    path('approve-med-cert/', views.approve_med_cert_request, name='approve-med-cert'),
    path('view-med-cert/<int:certificate_id>/', views.view_medical_certificate, name='view-med-cert'),


    path('api/monthly-model-counts/', views.monthly_model_counts, name='monthly_model_counts'),
    path('api/model-counts/', views.model_counts, name='model_counts'),





    path('approve-user-request/<int:user_id>/', views.approve_user_request, name='approve-user-request'),
    path('reject-user-request/<int:user_id>/', views.reject_user_request, name='reject-user-request'),

            # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
