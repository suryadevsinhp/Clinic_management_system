from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.views.generic import ListView
from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login , logout , authenticate

# Create your views here.

# yT Hospital management 

def aboutUs(request):
    return render (request,'aboutUs.html')

def home(request):
    return render(request,'home.html')

def index(request):
    return render(request,'index.html')

def contactus(request):
    return render(request,'contactus.html')

def index(request):
    if not request.user.is_authenticated:
        return redirect('/login_admin/')
    return render(request,'index.html')

def login_admin(request):
    error = ""
    if request.method == "POST":
        user_name = request.POST['username']
        user_password = request.POST['password']
        user = authenticate(username=user_name, password=user_password)
        try:
            if user.is_authenticated:
                login(request,user)
                error = "no"
            else:
                error="yes"
        except:
            error="yes"
    # else:
    #     return render(request,"login.html")
    d={'error': error}
    return render(request,"login.html",d)

def logout_admin(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    logout(request)
    return redirect('login_admin')

            

    
def view_patient(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    patients = Patient.objects.all()
    pat_obj = {'patient' : patients}
    return render(request,'viewPatient.html',pat_obj)  


def updatePatient(request,pid):
    patient = Patient.objects.get(patient_id = pid)
    form = Patient_form(instance=patient)
    if request.method=='POST':
        form =Patient_form(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('viewPatients') 
    else:
        args =Patient_form(instance=patient)
        return render(request,'savePatient.html',{'args':args})        


def delete_patient(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    patient = Patient.objects.filter(patient_id=pid)
    patient.delete()    
    remaining_patients = Patient.objects.all()
    return render(request, 'viewPatient.html',{ 'patient' : remaining_patients })


   
def view_appointment(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    appointment = Appointment.objects.all()
    p_name = Patient.objects.all()
    doc_name = Doctor.objects.all()
    return render(request,'viewAppointment.html', {'appointment':appointment, 'p_name':p_name, 'doc_name':doc_name})

def delete_appointment(request, aid):
    if not  request.user.is_authenticated:
        return redirect('login_admin')
    app = Appointment.objects.filter(appointment_id = aid)
    app.delete()
    return redirect('viewAppointment')

def view_prescription(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    prescription = Prescription.objects.all()
    return render (request,"viewPrescription.html",{"prescription":prescription})


def delete_prescription(request, presc_id):
    if not  request.user.is_authenticated:
        return redirect('login_admin')
    del_presc = Prescription.objects.filter(prescription_id=presc_id)
    del_presc.delete()
    return redirect('viewPrescription')

def view_billing(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    billing = Billing.objects.all()
    return  render(request,'viewBilling.html',{'billing':billing})

def delete_billing(request, bid):
    bill = Billing.objects.filter(bill_id=bid)
    bill.delete()
    return redirect('viewBilling')


def edit_patient(request, pid):
    pass


def all_details_display(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    display_patient = Patient.objects.filter(patient_id=pid)
    display_appointment = Appointment.objects.filter(Patient_id_id=pid)
    display_prescription = Prescription.objects.filter(patient_id_id=pid)
    return render (request,'allDetailsDisplay.html',{'display_patient': display_patient,'display_appointment': display_appointment, 'display_prescription': display_prescription })
    




#=======================================================


class PatientListView(ListView):
    #this class is made for displaying patents added data
    model = Patient
    template_name = 'patient_list.html'  # Replace with your template name
    context_object_name = 'patients'

def addNewPatient(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    return render(request,'savePatient.html',)


def home_page(request):
    return render(request,'home_page.html')

# view for all save patients is below:
# # #------------ * Html form is used to get form data * ---------------------------
def save_patient(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
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
        return redirect('viewPatient')
        
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


'''# === ADD, UPDATE, VIEW, DELETE VIEW FOR DOCTOR IS CREATED HERE =========='''

def addDoctor(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    if request.method == 'POST':
        docForm = Doctor_form(request.POST)
        if docForm.is_valid():
            docForm.save()
            return redirect('viewDoctor')
               
    else:
        docForm = Doctor_form()
        return render(request, 'saveDoctor.html', {'docForm': docForm})
    return render(request, 'saveDoctor.html', {'docForm': docForm})


# update doctor view:

def updateDoctor(request, did):
    doctors = Doctor.objects.get(doctor_id=did)
    if request.method=='POST':
        docForm = Doctor_form(request.POST, instance=doctors)
        if docForm.is_valid():
            docForm.save()
            return redirect('viewDoctor')
    else:
        docForm = Doctor_form(instance=doctors)
    return render(request,'saveDoctor.html',{'docForm':docForm})



def view_doctor(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    doctors = Doctor.objects.all()
    doc_obj = { 'doctor' : doctors }
    return render(request, 'viewDoctor.html',doc_obj) 


def delete_doctor(request, did):
    if not request.user.is_authenticated:
        return redirect('login_admin') 
    doctor = Doctor.objects.filter(doctor_id=did)
    doctor.delete()    
    # remaining_doctors = Doctor.objects.all()
    # return render(request, 'viewDoctor.html', {'doctor': remaining_doctors})  # # to skip this 2 lines we can use direct redirect() and return html page 
    return redirect('viewDoctor')

# view for all Appointment is below:
def addAppointment(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
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
    if not request.user.is_authenticated:
        return redirect('login_admin')
    submitted = False
    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('viewPrescription')
    else:
        form = PrescriptionForm
        if 'submitted' in request.GET:
            submitted=True
    
    return render(request,'savePrescription.html', {'form':form, 'submitted':submitted})


# view for billimg
def addBilling(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('viewBilling')
        
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
    if not request.user.is_authenticated:
        return redirect('login_admin')
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




