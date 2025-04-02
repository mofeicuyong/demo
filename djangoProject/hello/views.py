from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.
# hello/views.py



def hello_page(request):
    return render(request, 'hello.html')

@api_view(['PUT'])
def getData(request):
    return Response()