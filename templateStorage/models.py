from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import ModelForm, Textarea, TextInput, FileInput


# Create your models here.

class ContractTemplate(models.Model):
    original_file = models.FileField(upload_to='templates/', validators=[FileExtensionValidator(allowed_extensions=['docx'])])
    text_content = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContractTemplateForm(ModelForm):
    class Meta:
        model = ContractTemplate
        fields = ['name', 'description', 'original_file']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'form-control'}),
            'original_file': FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Name of the template',
            'description': 'Description of this template',
            'original_file': 'Choose a file (.docx)'
        }
