from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Strategy

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    strategies = Strategy.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'strategies': strategies})