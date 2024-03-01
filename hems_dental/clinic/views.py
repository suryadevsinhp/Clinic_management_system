from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.views.generic import ListView
from .models import *
from .forms import *

# Create your views here.

# yT Hospital management 
def aboutUs(request):
    return render (request,'aboutUs.html')

def home(request):
    return render(request,'home.html')

def contactus(request):
    return render(request,'contactus.html')







#=======================================================


class PatientListView(ListView):
    #this class is made for displaying patents added data
    model = Patient
    template_name = 'patient_list.html'  # Replace with your template name
    context_object_name = 'patients'

def addNewPatient(request):
    return render(request,'savePatient.html',)


def home_page(request):
    return render(request,'home_page.html')

# view for all save patients is below:
# # #------------ * Html form is used to get form data * ---------------------------
def save_patient(request):
    if request.method == "POST":
        name=request.POST.get('patient_name')
        dob =request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        blood_group = request.POST.get("blood_group")
        email = request.POST.get("email_id")
        address=request.POST.get("address")
        mob = request.POST.get("mobile_number")
        new_patient = Patient(name=name, date_of_birth=dob,gender=gender,blood_group=blood_group,email_id=email,address=address,mobile_number=mob)
        new_patient.save()
        return HttpResponse ("Data saved")
        
    return render( request,'savePatient.html')


# # #------------ * Django forms is used to get form data * ---------------------------
# # doctors entery form is created here:
# def addDoctor(request):
#     if request.method == 'POST':
#         docForm = Doctor_form(request.POST)
#         if docForm.is_valid():
#             docForm.name = docForm.cleaned_data['name']
#             docForm.age = docForm.cleaned_data['age']
#             docForm.gender = docForm.cleaned_data['gender']
#             docForm.experince = docForm.cleaned_data['experince']
#             docForm.languages = docForm.cleaned_data['languages']
#             docForm.mobile_number = docForm.cleaned_data['mobile_number']
#             docForm.email = docForm.cleaned_data['email']
#             docForm.schedule = docForm.cleaned_data['schedule']
#             docForm.save()
#             return HttpResponse("Doctor form is valid")
    
#     else:
#         docForm = Doctor_form()
    
#     return render(request,"saveDoctor.html",{'docForm':docForm})

# === NEW DOCTOR ADD VIEW IS CREATED HERE ==========

def addDoctor(request):
    if request.method == 'POST':
        docForm = Doctor_form(request.POST)
        if docForm.is_valid():
            docForm.save()
            return HttpResponse('success')
               
    else:
        docForm = Doctor_form()
        return render(request, 'saveDoctor.html', {'docForm': docForm})
    return render(request, 'saveDoctor.html', {'docForm': docForm})



# view for all Appointment is below:
def addAppointment(request):
    if request.method =='POST':
        appForm = AppointmentForm(request.POST)
        if appForm.is_valid():
            appForm.save()
            return HttpResponse("Appointment is saved")
    
    else:
        appForm=AppointmentForm()
        return render(request, 'saveAppointment.html', {'appForm':appForm} )
    return render(request, 'saveAppointment.html', {'appForm':appForm} )


# view for all Prescription is below:
def addPrescription(request):
    submitted = False
    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Prescription is saved")
    else:
        form = PrescriptionForm
        if 'submitted' in request.GET:
            submitted=True
    
    return render(request,'savePrescription.html', {'form':form, 'submitted':submitted})


# view for billimg
def addBilling(request):
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Billing Data is saved sucessfully")
        
    else:
        form = BillingForm
        
    return render(request,'saveBilling.html',{'form':form})


#view for review

def addReview(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Review is saved successfully")
        
    else:
        form = ReviewForm

    return render(request, 'SaveReview.html', {'form':form})
    



# view for all details is below:
def allDetails(request,id):
    if request.method=='POST':
        patientID= request.POST.get('patientID')
        patient_obj = Patient.objects.get(patient_id=patientID)
        appointment_obj = Appointment.objects.get(Patient_id=patientID)
        return render(request,'allDetailsDisplay.html', {'patient_obj': patient_obj, 'appointment_obj':appointment_obj})
    try:
        patientID = request.GET.get("patientID")
        patient_obj = Patient.objects.get(patient_id=patientID)
        appointment_obj = Appointment.objects.get(Patient_id=patientID)
        return render(request,'allDetailsDisplay.html', {'patient_obj': patient_obj, 'appointment_obj':appointment_obj})
    except:
        return HttpResponse("No patient of this id found : ")
    




    


























































#         form = Patient_form(request.POST)
#         if form.is_valid():
#             patient_entery = Patient(
#                 name = form.cleaned_data["patient_name"],
#                 dob =form.cleaned_data["date_of_birth"],
#                 gender = form.cleaned_data["gender"],
#                 blood_group = form.cleaned_data["blood_group"],
#                 email = form.cleaned_data["email_id"],
#                 address=form.cleaned_data["address"],
#                 mob = form.cleaned_data["mobile_number"]
#             )
#             # new_patient =Patient(name=patient_entery)
#         return render(request,'savePatient.html')

#     else:
#         form = Patient_form() #empty form
#     return render(request, "patient_entery_form.html", {"form":form})
# # #  #-----------------------------------------------------------------------
    


#             #the commented part of code in not accepting data to models:




