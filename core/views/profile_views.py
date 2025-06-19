from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        # Add profile update logic here
        return redirect('dashboard')
    return render(request, 'profiles/edit.html')