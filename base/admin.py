from django.contrib import admin
from . models import *
# Register your models here.


admin.site.register(ClinicConsultation)
admin.site.register(BPMonitoring)
admin.site.register(DentalCase)
admin.site.register(Vaccination)
admin.site.register(AppointmentRequest)
admin.site.register(Appointment)
admin.site.register(MedicalCertificateRequest)

admin.site.register(MedicalCertificate)

