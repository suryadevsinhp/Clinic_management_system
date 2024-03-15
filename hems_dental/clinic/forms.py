from django import forms
from django.shortcuts import HttpResponse
from .models import *
from django.forms import ModelForm


class Doctor_form(ModelForm):
    class Meta:
        model = Doctor
        fields = "__all__"
        # fields = ('age', 'name', 'gender','experince','languages','mobile_number','email','schedule')
        # insted of u can use specific fields also using tupple like above


# appointment form 
class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"

# Prescription Form
class PrescriptionForm(ModelForm):
    class Meta:
        model = Prescription
        fields = "__all__"

        # fields = ('prescription_id', 'patient_id', 'medicine', 'advice')

# Billing form 

class BillingForm(ModelForm):
    class Meta:
        model = Billing
        fields = '__all__'



# Review form

class ReviewForm(ModelForm):
    class Meta:
        model = Review 
        fields = '__all__'


#form for patient data entery are made here .

class Patient_form(forms.Form):
    name = forms.CharField()
    dob = forms.DateInput()
    gender = forms.CharField()
    blood_group = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    address = forms.TextInput()
    mob = forms.IntegerField()

    def __str__(self) -> str:
        return Patient_form










# below doctor foem that is created is not working ====================================
    
# class Doctor_form(forms.Form):
#     name = forms.CharField(label="name")
#     age = forms.IntegerField(label="Age")
#     gender = forms.CharField(label="Gender")
#     experince = forms.IntegerField(label="Experince")
#     languages = forms.CharField(label="Known languages")
#     mobile_number = forms.IntegerField(max_value=9999999999, label="mobile number")
#     email = forms.EmailField(label="Your gmail")
#     schedule = forms.CharField(required=False,label="When to schedule appt. ")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


    

