from django.shortcuts import render
from django.http import HttpResponse
from .models import *
# Create your views here.


def home(request):
    return HttpResponse("Hello, world. You're at the home view od data entry.")

def data_view(request, data_id):
    return HttpResponse ("Hello, you are viewing data view/loging main page...! %s"   %data_id)

def patient_view(request,data_id):
    response = "you are looking at patient details of folllowing id : %s "
    return HttpResponse(response  %data_id )

def dataEntry(request):
    if request.method=='post':
        general=request.post.get['general']
        doctor_name=request.post.get['doctor_name']
        patient_name=request.post.get['patient_name']
        entry_time=request.post.get['entry_time']

        new_entry = All_entries(general=general,doctor_name=doctor_name,patient_name=patient_name,entry_time=entry_time)
        new_entry.save()

    return render(request,'dataEntry.html')
