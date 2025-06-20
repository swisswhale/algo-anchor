from django import forms
from django.contrib.auth.models import User
from .models import Strategy, Security
import yfinance as yf

class StrategyForm(forms.ModelForm):
    tickers = forms.CharField(
        required=True,
        help_text="Enter 1 to 5 ticker symbols separated by commas (e.g. AAPL, MSFT)",
        widget=forms.TextInput(attrs={
            'placeholder': 'AAPL, MSFT',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Strategy
        fields = ['name', 'lookback_days', 'entry_threshold', 'exit_rule', 'tickers']

    def clean_tickers(self):
        ticker_str = self.cleaned_data['tickers']
        tickers = [t.strip().upper() for t in ticker_str.split(',') if t.strip()]
        if not 1 <= len(tickers) <= 5:
            raise forms.ValidationError("You must enter between 1 and 5 tickers.")
        return tickers

    def save(self, commit=True):
        instance = super().save(commit=False)
        tickers = self.cleaned_data.get('tickers', [])

        if commit:
            instance.save()

        # Link tickers to strategy
        securities = []
        for symbol in tickers:
            security, _ = Security.objects.get_or_create(symbol=symbol)
            # optionally pull metadata from yfinance
            if not security.name or not security.market_cap:
                try:
                    info = yf.Ticker(symbol).info
                    security.name = info.get("shortName") or security.name
                    security.market_cap = info.get("marketCap")
                    security.sector = info.get("sector")
                    security.save()
                except Exception:
                    pass
            securities.append(security)

        instance.tickers.set(securities)
        
        return instance


class UserUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email