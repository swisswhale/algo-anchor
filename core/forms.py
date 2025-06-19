from django import forms
from core.models import Strategy
from django.contrib.auth.models import User

class StrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'lookback_days', 'entry_threshold', 'exit_rule']
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']