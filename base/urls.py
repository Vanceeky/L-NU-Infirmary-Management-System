from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('daily-logs/', views.daily_logs, name="daily-logs"),
    
    path('patients/', views.patients, name="patients"),
    path('patient-profile/', views.patient_profile, name="patient-profile"),

    path('inventory/', views.inventory, name="inventory"),
    path('appointments/', views.appointments, name="appointments"),


    path('search_patient/', views.patient_autocomplete, name="search-patient"),

    path('add-clinic-consultation-log/', views.add_clinic_consultation, name="add-clinic-consultation"),

    path('add-dental-case-log/', views.add_dental_case, name="add-dental-case"),

    path('add-bp-monitoring-log/', views.add_bp_monitoring, name="add-bp-monitoring"),

]
