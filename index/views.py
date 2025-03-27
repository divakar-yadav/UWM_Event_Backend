from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    # send a 200 response

    return HttpResponse("You found the srpc server", status=200)