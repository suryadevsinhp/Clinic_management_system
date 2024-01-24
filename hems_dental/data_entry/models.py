from django.db import models

# Models for data_entry i.e patient, doctor, medical representative, staff.

class All_entries(models.Model):
    general = models.CharField(max_length=60)
    doctor_name = models.CharField(max_length=60)
    patient_name = models.CharField(max_length=60)
    entry_time = models.DateTimeField()

    # def __str__(self):
    #     return self.general, self.doctor_name, self.patient_name

    def __str__(self) -> str:
        return self.general, self.patient_name, self.doctor_name, self.entry_time
 
class Data_entered(models.Model):
    person_id = models.ForeignKey(All_entries, on_delete=models.CASCADE)
    doctor_details = models.CharField(max_length=200)
    patient_details = models.CharField(max_length=200)

    def __str__(self) -> str:
       return Data_entered
   


'''

from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers

# Create your model for patient content
class Patient(models.Model):
    # Define the fields for patient id, name, date of birth, gender, blood group, email id, address, mobile number
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    blood_group = models.CharField(max_length=5, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')])
    email_id = models.EmailField()
    address = models.TextField()
    mobile_number = models.CharField(max_length=15)

    # Define a string representation for the model
    def __str__(self):
        return self.name

# Create a serializer for the model
class PatientSerializer(serializers.ModelSerializer):
    # Define the fields to be serialized
    class Meta:
        model = Patient
        fields = ['patient_id', 'name', 'date_of_birth', 'gender', 'blood_group', 'email_id', 'address', 'mobile_number']


'''