from django.shortcuts import render
from django.http import HttpResponseRedirect
from contracts.models import Contract
# Create your views here.


def index(request):
    nbr_pending = Contract.objects.filter(signed=False).count()
    nbr_stored = Contract.objects.filter(signed=True).count()

    context = {'pending': nbr_pending, 'stored': nbr_stored}

    return render(request, 'dashboard/index.html', context)


def change_role(request):
    if request.session.get('role') != 'lawyer':
        request.session['role'] = 'lawyer'
    else:
        request.session['role'] = 'sourcing'

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))