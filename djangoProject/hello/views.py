from django.shortcuts import render

# Create your views here.
# hello/views.py



def hello_page(request):
    return render(request, 'hello.html')
