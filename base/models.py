from django.db import models
from authentication.models import Patient

# Create your models here.


class ClinicConsultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    chief_complaint = models.TextField()
    remarks = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.chief_complaint} - {self.remarks}"

class BPMonitoring(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    heart_rate = models.IntegerField()
    remarks = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.systolic} - {self.diastolic} - {self.heart_rate}"

class DentalCase(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    treatment_needed = models.TextField()
    remarks = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.treatment_needed} - {self.remarks}"
    

class Vaccination(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    dose = models.CharField(max_length=100, choices=[ ('1st Dose / Booster', '1st Dose/Booster'), ('2nd Dose', '2nd Dose'), ('3rd Dose', '3rd Dose')])
    next_dose_due = models.DateField(null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.vaccine_name} - {self.dose} - {self.next_dose_due}"


class AppointmentRequest(models.Model):

    status_choices = [

        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Missed', 'Missed'),
        ('Completed', 'Completed'),
        ('In Progress', 'In Progress'),
        ('In Queue', 'In Queue'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    remarks = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=status_choices, default='Pending')

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.patient} - {self.reason} - {self.status}"
    

class Appointment(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    purpose = models.TextField()
    remarks = models.TextField(null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.purpose}"


    

class MedicalCertificateRequest(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    purpose = models.CharField(max_length=100)
    reason = models.TextField()
    additional_notes = models.TextField(null=True, blank=True)
    additional_file = models.FileField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Issued', 'Issued'), ('Denied', 'Denied')], default='Pending')


    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.purpose} - {self.status}"
    

class MedicalCertificate(models.Model):
    
    request_id = models.ForeignKey(MedicalCertificateRequest, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    remarks = models.TextField(null=True, blank=True)

    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)


    status = models.CharField(max_length=12, choices=[('Pending', 'Pending'), ('Issued', 'Issued'), ('Received', 'Received')], default='Pending')


    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.purpose} - {self.status}"