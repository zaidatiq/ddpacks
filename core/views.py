from django.shortcuts import render

# Create your views here.

def my_name_view(request):
    return render(request, 'index.html')
