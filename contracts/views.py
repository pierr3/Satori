from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import ContractForm, Contract, Version, VersionForm, Amendment
from mammoth import extract_raw_text
from names import get_first_name
from diff_match_patch import diff
# Create your views here.


def create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)

        if form.is_valid():

            # Create an empty version
            contract = form.save()

            version = Version.create_from_template(request.POST.get('template_id'), contract)
            version.uploaded_by = get_first_name()
            version.save()

            return HttpResponseRedirect('/contracts/view/'+str(contract.pk))

    else:
        form = ContractForm()

    context = {'form': form}

    return render(request, 'contracts/create.html', context)


def pending(request):
    context = {'contracts': Contract.objects.filter(signed=False).all()}

    return render(request, 'contracts/pending.html', context)


def stored(request):
    context = {'contracts': Contract.objects.filter(signed=True).all()}

    return render(request, 'contracts/stored.html', context)


def sign(request, contract_id):
    Contract.objects.select_for_update().filter(id=contract_id).update(signed=True)

    return render(request, 'contracts/docusign.html', {'contract_id': contract_id})


def insert_html(string, index, insertion):
    return string[:index] + insertion + string[index:]


def build_changes_display(display_version):
    # Html stuff
    html_mark_open = "<mark>"
    html_mark_close = "</mark>"

    html_tooltip_deleted = '&nbsp;<button type="button" class="btn btn-sm btn-danger" data-container="body" data-toggle="popover"' + \
                           'data-placement="top" data-content="<<change>>" data-original-title="" title="">' + \
                           '<i class="fa fa-times-circle-o"></i></button>&nbsp;'

    output = display_version.text

    index_offset = 0

    for amendment in display_version.amendment_set.all():
        # If the amendment is not pending, we don't show it
        if not amendment.pending:
            pass

        # If the amendment contains a new version, aka, not just a deletion
        if len(amendment.amended) != 0:
            output = insert_html(output, amendment.start_position + index_offset, html_mark_open)
            index_offset += len(html_mark_open)
            output = insert_html(output, amendment.end_position + index_offset, html_mark_close)
            index_offset += len(html_mark_close)
        else:
            # If the amendment is just a deletion
            tooltip = html_tooltip_deleted.replace('<<change>>', amendment.original)
            output = insert_html(output, amendment.start_position + index_offset, tooltip)
            index_offset += len(tooltip)

    return output.replace("\n", "<br>")


def view(request, contract_id, contract_version=0):
    contract = Contract.objects.get(pk=contract_id)

    display_version = contract.version_set.last()
    if contract_version != 0:
        display_version = contract.version_set.get(pk=contract_version)

    upload_version_form = VersionForm()

    context = {'contract': contract, 'display_version': display_version,
               'changes_display': build_changes_display(display_version),
               'versions': contract.version_set.order_by('-created_at'),
               'upload_version_form': upload_version_form}

    return render(request, 'contracts/view.html', context)


def make_amendments(contract, new_version):
    old_version = contract.version_set.order_by('-updated_at')[1]

    changes = diff(old_version.text, new_version.text,
                   timelimit=0, checklines=False)

    cursor_old = 0
    cursor_new = 0

    working = False

    old_text_temp = ""
    old_text_length = 0

    for op, length in changes:
        if op == "=":
            print("next", length, "characters are the same")
            # No change for the next few characters

            # If we are working but we reach here, the last change was just a deletion, so we save it
            if working:
                Amendment.create_and_save(new_version, old_text_temp, "", cursor_new, cursor_new + old_text_length)
                working = False

            cursor_old += length
            cursor_new += length

        if op == "-":
            print("next", length, "characters are deleted")
            # Some text is deleted, we need to save it to add it to an amendment
            old_text_temp = old_version.text[cursor_old:cursor_old+length]
            old_text_length = length
            working = True

            cursor_old += length

        if op == "+":
            print("next", length, "characters are added")
            # Some text is added, we save it either way, and check if we were working
            new_text = new_version.text[cursor_new:cursor_new+length]
            if working:
                # If we were working, we save the old changed text
                Amendment.create_and_save(new_version, old_text_temp, new_text, cursor_new, cursor_new+length)
                working = False
            else:
                # If not, we just save the new text
                Amendment.create_and_save(new_version, "", new_text, cursor_new, cursor_new+length)

            cursor_new += length


def upload_version(request, contract_id):
    if request.method == 'POST':
        form = VersionForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)

            # process the form data to extract the word document text
            obj.text = extract_raw_text(obj.file).value
            obj.contract = Contract.objects.get(pk=contract_id)
            obj.uploaded_by = get_first_name()
            obj.save()

            make_amendments(obj.contract, obj)

    return HttpResponseRedirect('/contracts/view/'+str(contract_id))
