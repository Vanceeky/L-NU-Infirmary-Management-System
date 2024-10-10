from django.contrib import admin
from . models import *
from authentication.models import Patient
# Register your models here.


# Define inlines for each model

class ClinicConsultationInline(admin.TabularInline):
    model = ClinicConsultation
    extra = 1

class BPMonitoringInline(admin.TabularInline):
    model = BPMonitoring
    extra = 1

class DentalCaseInline(admin.TabularInline):
    model = DentalCase
    extra = 1

class VaccinationInline(admin.TabularInline):
    model = Vaccination
    extra = 1


class MedicineRestockInline(admin.TabularInline):
    model = MedicineRestock
    extra = 1

class MedicineUsageInline(admin.TabularInline):
    model = MedicineUsage
    extra = 1

# Define the PatientAdmin
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_id_number', 'contact_number', 'age', 'gender', 'category', 'designation')
    inlines = [
        ClinicConsultationInline,
        BPMonitoringInline,
        VaccinationInline,
        DentalCaseInline,
        MedicineUsageInline,
    ]

# Define the MedicalCertificateAdmin
admin.site.register(MedicalCertificate)
admin.site.register(Appointment)

admin.site.register(AppointmentRequest)
admin.site.register(MedicalCertificateRequest)


# Define the MedicineAdmin
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_in_stock', 'unit_of_measure', 'expiration_date')
    inlines = [MedicineRestockInline]


admin.site.site_title = 'L-NU Infirmary Administration'
admin.site.site_header = 'L-NU Infirmary'



