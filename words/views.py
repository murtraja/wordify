from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index(request):
    context_dict = {"boldmessage":"some bold message"}
    return render(request, 'words/index.html', context_dict)
