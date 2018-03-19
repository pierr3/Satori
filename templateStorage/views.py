from django.shortcuts import render
from .models import ContractTemplate, ContractTemplateForm
from django.http import HttpResponseRedirect, HttpResponse
import mammoth


# Create your views here.
def index(request):
    if request.method == 'POST':
        form = ContractTemplateForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)

            # process the form data to extract the word document text

            obj.text_content = mammoth.extract_raw_text(obj.original_file).value
            obj.save()

            return HttpResponseRedirect('/templates')
    else:
        form = ContractTemplateForm()

    all_templates = ContractTemplate.objects.order_by('-created_at')
    context = {'all_templates': all_templates, 'form': form}

    return render(request, 'templateStorage/index.html', context)


def delete(request):
    ContractTemplate.objects.filter(id=request.GET.get('id', '')).delete()
    return HttpResponseRedirect('/templates')
