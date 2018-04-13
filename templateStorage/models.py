from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import ModelForm, Textarea, TextInput, FileInput, ModelChoiceField, Select


# Create your models here.

class ContractCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ContractTemplate(models.Model):
    original_file = models.FileField(upload_to='templates/', validators=[FileExtensionValidator(allowed_extensions=['docx'])])
    text_content = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    category = models.ForeignKey(ContractCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContractTemplateForm(ModelForm):
    category = ModelChoiceField(queryset=ContractCategory.objects.all(), widget=Select(attrs={'class': 'form-control'}),
                                empty_label="(Nothing)")

    class Meta:
        model = ContractTemplate
        fields = ['name', 'description', 'category', 'original_file']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(attrs={'class': 'form-control'}),
            'original_file': FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Name of the template',
            'description': 'Description of this template',
            'original_file': 'Choose a file (.docx)',
            'category': 'Choose a category for this template'
        }
