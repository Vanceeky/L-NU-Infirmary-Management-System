from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_id_number = models.CharField(max_length=20, unique=True, null = True, blank = True)
    contact_number = models.CharField(max_length=13)
    age = models.CharField(max_length=3, null = True, blank = True)
    gender = models.CharField(max_length=6)
    category = models.CharField(max_length=8)
    designation = models.CharField(max_length=100)
    proof = models.FileField(upload_to='proofs/')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='/L-NU_LOGO.png')
    address = models.TextField(null=True, blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name} - {self.category}: {self.designation}"






