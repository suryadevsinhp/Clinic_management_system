from django.urls import path
from .views import *
from .forms import *


urlpatterns = [
    path('',home_page, name='home_page'),
    path('aboutUs/', aboutUs, name='aboutUs'),

    path('patiententry/',save_patient, name="patient_entery"),
    path('doctor/', addDoctor, name='addDoctor'),
    # path('addNewDoctor/', addNewDoctor, name='addNewDoctor'),
    path('allDetails/', allDetails, name='allDetails'),
    # path('allDetails/<int:patientID>', allDetails, name='allDetails'),
    path('addNewPatient/', addNewPatient, name='addNewPatient'),
    path('addAppointment/', addAppointment, name='addAppointment'),
    path('addPrescription/', addPrescription, name='addPrescription'),
    path('addBilling/', addBilling, name='addBilling'),
    path('addReview/', addReview, name='addReview'),


    
    # path('patients/', PatientListView.as_view(), name='patient-list'),
    # path('patientform/',Patient_form),
    # path('doctorform/',Doctor_form)


    # Add other URL patterns as needed
]
