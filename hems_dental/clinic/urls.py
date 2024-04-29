from django.urls import path
from .views import * 
from .forms import *


urlpatterns = [
    # yt
    path('home/',home,name ='home'),
    path('aboutus/', aboutUs, name='aboutUs'),
    path('contactus/', contactus, name='contactus'),
    
    path('login_admin/', login_admin, name='login_admin'),
    path('logout_admin/', logout_admin, name='logout_admin'),
    path('index/', index, name='index'),
    path('viewDoctor/', view_doctor, name='viewDoctor'),
    path('viewPatient/', view_patient, name='viewPatient'),
    path('viewAppointment/', view_appointment, name='viewAppointment'),
    path('viewPrescription/', view_prescription, name='viewPrescription'),
    path('viewBilling/', view_billing, name='viewBilling'),

    # update
    path('updateDoctor/<int:did>/', updateDoctor, name= 'updateDoctor'),
    path('updatePatient/<int:pid>/',updatePatient, name='updatePatient'),
    path('deletePatient/<int:pid>/', delete_patient, name='deletePatient'),
    path('deleteDoctor/<int:did>/', delete_doctor, name='deleteDoctor'),
    path('deleteAppointment/<int:aid>/', delete_appointment, name='deleteAppointment'),
    path('deletePrescription/<int:presc_id>/', delete_prescription, name='deletePrescription'),
    path('deleteBilling/<int:bid>/', delete_billing, name='deleteBilling'),
    path('allDetailsDisplay/<int:pid>/', all_details_display, name='allDetailsDisplay'),
    path('editPatient/<int:pid>/', edit_patient, name='editPatient'),





    # ---------------------
    path('',home_page, name='home_page'),
    path('index',index, name='index'),
 
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
