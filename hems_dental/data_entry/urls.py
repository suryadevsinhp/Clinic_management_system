from django.urls import path
from . import views

urlpatterns = [
    #shows main page i.e data entry view
    path('home',views.home, name='home'),
    #bellow url is for data_entry
    path('data_view/<int:data_id>/',views.data_view, name='data_view' ),
    #below for patient details
    path('patient_view/<int:data_id>/', views.patient_view, name='patient_view'),
    path('dataEntry',views.dataEntry, name='dataEntry'),

]
