from django.contrib import admin
from .models import Customer, Service, Bill

admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(Bill)