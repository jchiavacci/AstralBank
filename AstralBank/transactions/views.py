from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import TransactionForm


def model_form_upload(request):
    if request.method == "POST":
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            form.parse_transactions(request.FILES['file'])
            return HttpResponseRedirect('/admin')
    else:
        form = TransactionForm()
        return render(request, '/transactions/model_form_upload.html', {'form': form})
