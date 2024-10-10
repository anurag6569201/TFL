from django.shortcuts import render

def home(request):
    return render(request, 'apps/home/index.html')

def add_to_cart(request):
    return render(request, 'apps/home/add_to_cart.html')