from django.shortcuts import render
from .models import ContractTemplate, ContractTemplateForm, ContractCategory
from django.http import HttpResponseRedirect
from mammoth import extract_raw_text


# Create your views here.
def index(request):
    if request.method == 'POST':
        form = ContractTemplateForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)

            # process the form data to extract the word document text

            obj.text_content = extract_raw_text(obj.original_file).value
            obj.save()

            return HttpResponseRedirect('/templates')
    else:
        form = ContractTemplateForm()

    categories = ContractCategory.objects.all()
    context = {'categories': categories, 'form': form}

    return render(request, 'templateStorage/index.html', context)


def delete(request):
    ContractTemplate.objects.filter(id=request.GET.get('id', '')).delete()
    return HttpResponseRedirect('/templates')
