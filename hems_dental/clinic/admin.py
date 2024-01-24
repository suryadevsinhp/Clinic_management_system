from django.contrib import admin
from .views import Patient
from .models import Patient,Admin,Appointment,Billing,Doctor,Prescription,Review

# Register your models here.

admin.site.register(Patient)
admin.site.register(Admin)
admin.site.register(Appointment)
admin.site.register(Billing)
admin.site.register(Doctor)
admin.site.register(Prescription)
admin.site.register(Review)