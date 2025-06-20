from django import forms
from django.contrib.auth.models import User
from .models import Strategy, Security
import yfinance as yf

class StrategyForm(forms.ModelForm):
    tickers = forms.CharField(
        required=True,
        label="Securities",
        help_text="Enter 1 to 5 ticker symbols separated by commas (e.g. AAPL, MSFT, GOOGL)",
        widget=forms.TextInput(attrs={
            'placeholder': 'AAPL, MSFT, GOOGL',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Strategy
        fields = ['name', 'lookback_days', 'entry_threshold', 'exit_rule']
        labels = {
            'name': 'Strategy Name',
            'lookback_days': 'Lookback Period (Days)',
            'entry_threshold': 'Entry Threshold',
            'exit_rule': 'Exit Rule',
        }
        help_texts = {
            'name': 'A descriptive name for your strategy',
            'lookback_days': 'Number of days for moving average calculation (10-50 typical)',
            'entry_threshold': 'Z-score threshold for entry signal (-2 to -1 typical)',
            'exit_rule': 'When to exit the position (e.g., mean_revert, stop_loss, time_based)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'My Mean Reversion Strategy'}),
            'lookback_days': forms.NumberInput(attrs={'min': 5, 'max': 100, 'value': 20}),
            'entry_threshold': forms.NumberInput(attrs={'step': 0.1, 'min': -5, 'max': 5, 'value': -2}),
            'exit_rule': forms.TextInput(attrs={'placeholder': 'mean_revert'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # If editing an existing strategy, populate tickers field
        if self.instance.pk:
            existing_tickers = list(self.instance.tickers.values_list('symbol', flat=True))
            self.fields['tickers'].initial = ', '.join(existing_tickers)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError("Strategy name must be at least 3 characters long.")
        return name

    def clean_lookback_days(self):
        lookback_days = self.cleaned_data.get('lookback_days')
        if lookback_days and (lookback_days < 5 or lookback_days > 100):
            raise forms.ValidationError("Lookback days must be between 5 and 100.")
        return lookback_days

    def clean_entry_threshold(self):
        threshold = self.cleaned_data.get('entry_threshold')
        if threshold and (threshold < -5 or threshold > 5):
            raise forms.ValidationError("Entry threshold must be between -5 and 5.")
        return threshold

    def clean_tickers(self):
        ticker_str = self.cleaned_data['tickers']
        tickers = [t.strip().upper() for t in ticker_str.split(',') if t.strip()]
        
        if not 1 <= len(tickers) <= 5:
            raise forms.ValidationError("You must enter between 1 and 5 tickers.")
        
        # Validate ticker format (basic check)
        import re
        for ticker in tickers:
            if not re.match(r'^[A-Z]{1,5}$', ticker):
                raise forms.ValidationError(f"'{ticker}' is not a valid ticker symbol. Use 1-5 letters only.")
        
        return tickers

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Process tickers and create Security objects
        tickers = self.cleaned_data.get('tickers', [])
        print(f"DEBUG: Tickers from cleaned_data: {tickers}")
        securities = []
        for symbol in tickers:
            security, created = Security.objects.get_or_create(symbol=symbol)
            if created or not security.name:
                try:
                    info = yf.Ticker(symbol).info
                    security.name = info.get("longName") or info.get("shortName") or symbol
                    security.market_cap = info.get("marketCap")
                    security.sector = info.get("sector")
                    security.save()
                except Exception:
                    if not security.name:
                        security.name = symbol
                        security.save()
            securities.append(security)
        print(f"DEBUG: Securities created: {[s.symbol for s in securities]}")
        
        if commit:
            instance.save()
            # Set the tickers immediately since we're committing
            instance.tickers.set(securities)
            print(f"DEBUG: Tickers assigned to strategy (commit=True), count: {instance.tickers.count()}")
        else:
            # Store securities for later assignment
            instance._pending_tickers = securities
            print(f"DEBUG: Tickers stored for later assignment (commit=False)")
        
        return instance

    def save_m2m(self):
        print("ENTERING CUSTOM SAVE_M2M METHOD")
        # First call parent save_m2m to handle any actual ModelForm M2M fields
        super().save_m2m()
        print("FINISHED CALLING PARENT SAVE_M2M")
        
        # Then handle our custom pending tickers
        if hasattr(self.instance, '_pending_tickers'):
            print(f"DEBUG: Found pending tickers: {[s.symbol for s in self.instance._pending_tickers]}")
            self.instance.tickers.set(self.instance._pending_tickers)
            print(f"DEBUG: Tickers assigned in save_m2m, count: {self.instance.tickers.count()}")
            del self.instance._pending_tickers
        else:
            print("DEBUG: No pending tickers found in save_m2m")
        print("EXITING CUSTOM SAVE_M2M METHOD")


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