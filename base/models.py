from django.db import models
from authentication.models import Patient
from django.utils import timezone

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
        ('Notified', 'Notified'),
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
    
    request_id = models.ForeignKey(MedicalCertificateRequest, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    remarks = models.TextField(null=True, blank=True)

    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    date_received = models.DateTimeField(null=True, blank=True)

    def mark_as_received(self):
        self.date_received = timezone.now() 
        self.status = 'Received' 
        self.save()  

    status = models.CharField(max_length=12, choices=[('Pending', 'Pending'), ('Issued', 'Issued'), ('Received', 'Received')], default='Pending')


    def __str__(self):
        return f"{self.date_created} - {self.patient} - {self.purpose} - {self.status}"



class Medicine(models.Model):
    name = models.CharField(max_length=100)  # Name of the medicine
    quantity_in_stock = models.IntegerField()  # Current stock level
    unit_of_measure = models.CharField(max_length=50, default='tablets')  # Unit (e.g., tablets, ml)
    expiration_date = models.DateField(null=True, blank=True)  # Optional expiration date
    description = models.TextField(null=True, blank=True)  # Optional description

    def __str__(self):
        expiration_info = f"Expires on: {self.expiration_date.strftime('%Y-%m-%d')}" if self.expiration_date else "No expiration date"
        return f"{self.name} | Stock: {self.quantity_in_stock} {self.unit_of_measure} | {expiration_info}"


class MedicineUsage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)  # The patient receiving the medicine
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)  # The medicine being used
    quantity_used = models.IntegerField()  # How much of the medicine was used
    date_given = models.DateTimeField(auto_now_add=True)  # Automatically set the date of administration
    remarks = models.TextField(null=True, blank=True)  # Optional remarks (e.g., dosage instructions)

    def __str__(self):
        return f"{self.date_given} - {self.patient} was given {self.quantity_used} {self.medicine.unit_of_measure} of {self.medicine.name}"

    def save(self, *args, **kwargs):
        # Subtract the used quantity from the medicine stock
        self.medicine.quantity_in_stock -= self.quantity_used
        if self.medicine.quantity_in_stock < 0:
            self.medicine.quantity_in_stock = 0  # Prevent negative stock
        self.medicine.save()
        super().save(*args, **kwargs)


class MedicineRestock(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)  # The medicine being restocked
    quantity_added = models.IntegerField()  # How much was restocked
    date_restocked = models.DateTimeField(auto_now_add=True)  # Automatically set the date of restock
    remarks = models.TextField(null=True, blank=True)  # Optional remarks (e.g., batch number)

    def __str__(self):
        return f"{self.date_restocked} - Restocked {self.quantity_added} {self.medicine.unit_of_measure} of {self.medicine.name}"

    def save(self, *args, **kwargs):
        # Add the restocked quantity to the medicine stock
        self.medicine.quantity_in_stock += self.quantity_added
        self.medicine.save()
        super().save(*args, **kwargs)