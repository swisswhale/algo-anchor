from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import UserUpdateForm
from django.contrib import messages

@login_required
def profile_view(request):
    return render(request, 'profile/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'profile/edit_profile.html', {'form': form})