from django.contrib import admin
from .models import Patient, Doctor, Appointment, Prescription, Admin, Billing, Review, StaffProfile

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Admin)
admin.site.register(Billing)
admin.site.register(Review)
admin.site.register(StaffProfile)