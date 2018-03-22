from django.shortcuts import render
from .models import ContractForm, Contract, Version
# Create your views here.


def create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)

        if form.is_valid():

            # Create an empty version
            contract = form.save()

            version = Version.create_from_template(request.POST.get('template_id'), contract)
            version.save()

            form = ContractForm()

    else:
        form = ContractForm()

    context = {'form': form}

    return render(request, 'contracts/create.html', context)


def pending(request):
    context = {'contracts': Contract.objects.filter(signed=False).all()}

    return render(request, 'contracts/pending.html', context)


def view(request, contract_id):
    context = {'contract': Contract.objects.get(pk=contract_id)}

    return render(request, 'contracts/view.html', context)
