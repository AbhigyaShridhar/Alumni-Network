from django.contrib import admin
from .models import Person, Company, City

# Register your models here.
admin.site.register(Person)
admin.site.register(City)
admin.site.register(Company)
