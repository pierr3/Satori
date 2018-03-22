from django.shortcuts import render
from .models import ContractForm, Contract, Version
# Create your views here.


def create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)

        if form.is_valid():

            # Create an empty version
            contract = form.save()

            Version.create_from_template(request.POST.get('template_id'), contract)

            form = ContractForm()

    else:
        form = ContractForm()

    context = {'form': form}

    return render(request, 'contracts/create.html', context)


def pending(request):
    context = {'contracts': Contract.objects.filter(signed=False).all()}

    return render(request, 'contracts/pending.html', context)
