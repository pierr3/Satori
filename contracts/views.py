from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import ContractForm, Contract, Version, VersionForm, Amendment
from mammoth import extract_raw_text
from names import get_first_name
from diff_match_patch import diff
import spacy
from .utils import *


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


def build_changes_display(display_version):
    # Html stuff
    html_tooltip_deleted = "&nbsp;<mark class='deleted' data-container='body' " \
                           "data-toggle='popover' data-placement='top' data-content='{{content}}' " \
                           "title='{{title}}'>{{old_text}}</mark>&nbsp; "

    html_tooltip_changed_open = '<mark id="{{id}}"data-container="body" style="background-color:{{color}};" data-toggle="popover" data-placement="top" ' \
                                'data-content="{{content}}" title="{{title}}"> '
    html_tooltip_changed_close = '</mark>'

    output = display_version.text

    index_offset = 0

    for amendment in display_version.amendment_set.all():
        # If the amendment is not pending, we don't show it
        if not amendment.pending:
            pass

        # If the amendment contains a new version, aka, not just a deletion
        if len(amendment.amended) != 0:

            if len(amendment.original) != 0:
                content_change = "<b>Previous Text</b>: %s<br><br><b>Risk Value:</b> %s/100<br><br>" % (amendment.original, amendment.risk_value)
                title = "Text Change #%s" % amendment.id
            else:
                content_change = "Risk Value:</b> %s/100<br><br>" % amendment.risk_value
                title = "Text Addition #%s" % amendment.id

            if amendment.risk_value > 70:
                content_change += "<div class='alert alert-warning' role='alert'><b>This change has been escalated</b></div>"
            else:
                content_change += "<button class='btn btn-sm btn-success'>Accept</button>&nbsp;<button class='btn btn-sm btn-warning'>Escalate</button>&nbsp;<button class='btn btn-sm btn-danger'>Reject</button>"

            changes = [("{{id}}", str(amendment.id)), ("{{title}}", title), ("{{color}}", pseudocolor(amendment.risk_value)), ("{{content}}", content_change)]

            tooltip = multi_replace(html_tooltip_changed_open, changes)

            output = insert_html(output, amendment.start_position + index_offset, tooltip)
            index_offset += len(tooltip)
            output = insert_html(output, amendment.end_position + index_offset, html_tooltip_changed_close)
            index_offset += len(html_tooltip_changed_close)
        else:
            # If the amendment is just a deletion
            changes = [("{{title}}", "Text Deletion #%s" % amendment.id), ("{{content}}", "<b>Content deleted!</b>"), ("{{old_text}}", amendment.original)]

            tooltip = multi_replace(html_tooltip_deleted, changes)
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
               'amendments': display_version.amendment_set.filter(pending=True),
               'upload_version_form': upload_version_form}

    return render(request, 'contracts/view.html', context)


def assess_risk(nlp, new_text, old_text):
    risk = 0

    doc = nlp(new_text)

    # We start off with the similarity between the old and the new text
    if len(old_text) != 0:
        old_doc = nlp(old_text)
        risk = (1.0-doc.similarity(old_doc)) * 100

    # We then adjust that value for special text
    for ent in doc.ents:

        # If a geographic word is inserted, big risk value as may related to jurisdiction
        if ent.label_ == "GPE":
            risk += 50

        # If name of a person, low risk
        if ent.label_ == "PERSON":
            risk -= 50

        # If name of a company, low risk
        if ent.label_ == "ORG":
            risk -= 40

        # If name of a legal document, very high risk
        if ent.label == "LAW":
            risk += 60

        # If change of value, medium risk
        if ent.label == "MONEY":
            risk += 30

    return max(0, min(risk, 100))


def make_amendments(contract, new_version):
    nlp = spacy.load('en')
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
            # No change for the next few characters

            # If we are working but we reach here, the last change was just a deletion, so we save it
            if working:
                risk = assess_risk(nlp, "", old_text_temp)
                Amendment.create_and_save(new_version, old_text_temp, "", cursor_new, cursor_new + old_text_length, risk)
                working = False

            cursor_old += length
            cursor_new += length

        if op == "-":
            # Some text is deleted, we need to save it to add it to an amendment
            old_text_temp = old_version.text[cursor_old:cursor_old+length]
            old_text_length = length
            working = True

            cursor_old += length

        if op == "+":
            # Some text is added, we save it either way, and check if we were working
            new_text = new_version.text[cursor_new:cursor_new+length]
            if working:
                # If we were working, we save the old changed text
                risk = assess_risk(nlp, old_text_temp, new_text)
                Amendment.create_and_save(new_version, old_text_temp, new_text, cursor_new, cursor_new+length, risk)
                working = False
            else:
                # If not, we just save the new text
                risk = assess_risk(nlp, "", new_text)
                Amendment.create_and_save(new_version, "", new_text, cursor_new, cursor_new+length, risk)

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
