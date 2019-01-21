from django.db import models
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm

from django import forms
    
class Offer(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="b",null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="s", null=True)
    asset_name = models.CharField(max_length=100)
    quantity = models.DecimalField(default=0, max_digits=20,decimal_places=4)
    unit = models.CharField(max_length=10)
    price = models.DecimalField(default=0, max_digits=30, decimal_places=10)
    
    GBP = 'GBP'
    USD = 'USD'
    BTC = 'BTC'
    CURRENCY_CHOICES = ((GBP, 'GBP'), (USD, 'USD'), (BTC, 'BTC'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=GBP)
    
    BUY = 'Buy'
    SELL = 'Sell'
    CONTRACT_CHOICES = ((BUY, 'BUY'),(SELL, 'SELL'))    
    contract_type = models.CharField(max_length=4, choices=CONTRACT_CHOICES, default=BUY)
    
    location = models.CharField(max_length=8)
    completion_date = models.DateField()
    contract = models.TextField()
   
class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email','password']


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

        
class OfferCreationForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['contract_type', 'asset_name', 'quantity', 'unit', 'price', 'currency', 'completion_date']
        