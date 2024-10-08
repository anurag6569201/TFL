from django.shortcuts import render

def home(request):
    return render(request, 'apps/home/index.html')