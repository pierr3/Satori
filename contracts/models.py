from django.db import models
from django.core.validators import FileExtensionValidator
from django.forms import ModelForm, Textarea, TextInput, FileInput, ChoiceField, Select
from templateStorage.models import ContractTemplate
from os import path
from uuid import uuid4
from django.utils import text

# Create your models here.


class Contract(models.Model):
    name = models.CharField(max_length=200)
    summary = models.TextField()
    importance = models.IntegerField()
    value = models.IntegerField()
    signed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def version_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s-%s.%s" % (text.get_valid_filename(instance.contract.name), str(uuid4())[:8], ext)
    return path.join('versions/', filename)


class Version(models.Model):
    text = models.TextField()
    file = models.FileField(upload_to=version_file_name, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    uploaded_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_template(cls, template_id, contract):
        template = ContractTemplate.objects.get(pk=template_id)
        version = cls(text=template.text_content, file=template.original_file, contract=contract)
        return version


class Amendment(models.Model):
    original = models.TextField()
    amended = models.TextField()
    start_position = models.IntegerField()
    end_position = models.IntegerField()
    risk_value = models.IntegerField()
    pending = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)

    @classmethod
    def create_and_save(cls, version, original_text, amended_text, start_position, end_position, risk_value):
        amendment = cls(original=original_text, amended=amended_text,
                        start_position=start_position, end_position=end_position, version=version, risk_value=risk_value)
        amendment.save()
        return amendment


class VersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ['file']

        widgets = {
            'file': FileInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'file': 'Please select the new version (.docx)',
        }


class ContractForm(ModelForm):
    template_id = ChoiceField(label='Select the template you would like to use',
                              widget=Select(attrs={'class': 'form-control'}),
                              choices=[])

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        self.fields['template_id'].choices = [(x.pk, x.name) for x in ContractTemplate.objects.all()]

    class Meta:
        model = Contract
        fields = ['name', 'summary', 'importance', 'value', 'template_id']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'summary': Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'form-control'}),
            'importance': Select(choices=((1, 'Low'), (2, 'Medium'), (3, 'High')), attrs={'class': 'form-control'}),
            'value': Select(choices=((1, '< £20,000'), (2, '£20,000 to £100,000'), (3, '£100,000 to £500,000'),
                                     (4, '> £500,000')), attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Name of the contract',
            'summary': 'Description of this contract',
            'importance': 'Rate the importance of this contract overall for the company',
            'value': 'Estimate the monetary value of the contract',
        }

