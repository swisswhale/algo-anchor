from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def strategy_list(request):
    """Display list of strategies"""
    return render(request, 'strategies/list.html')

def strategy_create(request):
    """Create new strategy"""
    if request.method == 'POST':
        # Add strategy creation logic here
        messages.success(request, 'Strategy created successfully!')
        return redirect('strategy_list')
    return render(request, 'strategies/create.html')

# Add missing views that are in urls.py
def strategy_detail(request, pk):
    """Display strategy details"""
    # strategy = get_object_or_404(Strategy, pk=pk)
    return render(request, 'strategies/detail.html')

def strategy_delete(request, pk):
    """Delete strategy"""
    # strategy = get_object_or_404(Strategy, pk=pk)
    if request.method == 'POST':
        # strategy.delete()
        messages.success(request, 'Strategy deleted successfully!')
        return redirect('strategy_list')
    return render(request, 'strategies/delete.html')