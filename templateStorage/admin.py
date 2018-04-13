from django.contrib import admin
from .models import ContractTemplate, ContractCategory

# Register your models here.

admin.site.register(ContractTemplate)
admin.site.register(ContractCategory)