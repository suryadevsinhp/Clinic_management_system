from django.db import models
from phonenumber_field import phonenumber # pip install phonenumber_field
from django.utils import timezone

# Hems Clinic Models are made here.

# class Login(models.Model):
#     patient = patient_id as username 
#     doctor = doctor_id as username
#     admin = admin_id as username

'''
Here we have to create models for registration, making appointment, cancel appointment, payment mode. Dr Model, patient module prescription module
'''

class Patient (models.Model):  
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    date_of_birth = models.DateField()
    # gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    gender = models.CharField(max_length=10)
    # blood_group = models.CharField(max_length=5, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')])
    blood_group = models.CharField(max_length=10)
    email_id = models.EmailField()
    address = models.TextField()
    mobile_number = models.CharField(max_length=15)
    
    def __str__(self) -> str:
        return self.name



class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    age = models.IntegerField()
    name = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    experince = models.IntegerField()
    languages = models.CharField(max_length=25)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    schedule = models.CharField(max_length=25, blank= True)
    def __str__(self) -> str:
        return self.name

class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key= True)
    Patient_id = models.ForeignKey(Patient,on_delete=models.CASCADE) 
    specialization = models.CharField(max_length=50)
    doctor_id = models.ForeignKey(Doctor,on_delete = models.CASCADE)
    consultation_fee = models.IntegerField()
    date = models.DateField(default=timezone.now().date(),null=True)
    # time = models.TimeField(null=True)

    def __str__(self) -> str:
        return self.Patient_id.name

class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor_id =  models.ForeignKey(Doctor ,on_delete=models.SET_NULL,blank=True,null=True)
    appointment_id = models.ForeignKey(Appointment,on_delete=models.SET_NULL,blank=True,null=True)
    medicine_name = models.CharField(max_length=200,  default='no specific medicine given')
    dosage = models.CharField(max_length=200,  default='no specific medicine given')
    duration = models.CharField(max_length=100,  default='no specific medicine given')
    diagnosis = models.CharField(max_length =250,  default='no specific medicine given')
    medicine = models.CharField(max_length=500, default='no specific medicine given')
    advice = models.CharField(max_length=100, default='no specific advice')
    def __str__(self) -> str:
        return self.prescription_id.name

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    date_of_birth = models.DateField(default=timezone.now)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Billing(models.Model):
    patient_id = models.ForeignKey(Patient,on_delete=models.CASCADE)
    bill_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now=True)
    amount = models.IntegerField(max_length=10)
    remarks = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.patient_id.name

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    review_data = models.CharField(max_length=999)

    def __str__(self) -> str:
        return self.patient_id.name


    



