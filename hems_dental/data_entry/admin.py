from django.contrib import admin
from data_entry.models import *


# Register your models here.

class Data_entry_admin(admin.ModelAdmin):
    display_data = ('general')

admin.site.register(All_entries,Data_entry_admin)
