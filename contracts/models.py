from django.db import models
from django.core.validators import FileExtensionValidator
from django.forms import ModelForm, Textarea, TextInput, IntegerField, ChoiceField, Select, ModelChoiceField
from templateStorage.models import ContractTemplate

# Create your models here.


class Contract(models.Model):
    name = models.CharField(max_length=200)
    summary = models.TextField()
    importance = models.IntegerField()
    value = models.IntegerField()
    signed = models.BooleanField(default=False)


class Version(models.Model):
    text = models.TextField()
    file = models.FileField(upload_to='versions/', validators=[FileExtensionValidator(allowed_extensions=['docx'])])
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_template(cls, template_id, contract):
        template = ContractTemplate.objects.get(pk=template_id)
        book = cls(text=template.text_content, file=template.original_file, contract=contract)
        return book


class Amendment(models.Model):
    original = models.TextField()
    amended = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)


class ContractForm(ModelForm):
    template_id = ChoiceField(label='Select the template you would like to use',
                              widget=Select(attrs={'class':'form-control'}),
                              choices=[(x.pk, x.name) for x in ContractTemplate.objects.all()])

    class Meta:
        model = Contract
        fields = ['name', 'summary', 'importance', 'value', 'template_id']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'summary': Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'form-control'}),
            'importance': Select(choices=((1, 'Low'), (2, 'Medium'), (3, 'High')), attrs={'class': 'form-control'}),
            'value': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Name of the contract',
            'summary': 'Description of this contract',
            'importance': 'Rate the importance of the contract for your company',
            'value': 'Estimate the monetary value of the contract in £',
        }

