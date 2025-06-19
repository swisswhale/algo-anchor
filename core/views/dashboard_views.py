from django.shortcuts import render

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def dashboard(request):
    """Dashboard view"""
    return render(request, 'dashboard/dashboard.html')