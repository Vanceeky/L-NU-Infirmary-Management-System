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