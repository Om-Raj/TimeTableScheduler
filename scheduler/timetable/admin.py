from django.contrib import admin
from .models import TimeTable, Slot, Section

# Register your models here.
admin.site.register(TimeTable)
admin.site.register(Slot)
admin.site.register(Section)
