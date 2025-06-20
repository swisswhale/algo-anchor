from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def profile_view(request):
    """Display user profile information"""
    context = {
        'user': request.user,
        'strategy_count': request.user.strategy_set.count(),
    }
    return render(request, 'profile/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile information"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Your password has been changed successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'profile/change_password.html', {'form': form})