from django.db import models
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.forms import UserCreationForm

from django import forms
    
class Offer(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="b",null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="s", null=True)
    asset_name = models.CharField(max_length=100)
    condition_help = "Keywords: <span class='keyword'>AND</span>, <span class='keyword'>OR</span>.</br>Operations: <, >, =</br>Variables: <span class='variable'>price</span>, <span class='variable'>quantity</span></br>Use parentheses to group statements.</br></br>Example:</br> (<span class='variable'>price</span> < 100 <span class='keyword'>AND</span> (<span class='variable'>quantity</span> > 20 <span class='keyword'>AND</span> <span class='variable'>quantity</span> < 50)) </br><span class='keyword'>OR</span> (<span class='variable'>price</span> < 120 <span class='keyword'>AND</span> <span class='variable'>quantity</span> < 20)"
    completion_condition = models.CharField(max_length=256, help_text=condition_help)
    
    #format: priceLow,priceHigh,quantLow,quantHigh|...|...
    bounds = models.CharField(max_length=256, default="0,{},0,{}".format(str(2**31), str(2**31)))
    
    unit = models.CharField(max_length=10)    
    GBP = 'GBP'
    USD = 'USD'
    BTC = 'BTC'
    CURRENCY_CHOICES = ((GBP, 'GBP'), (USD, 'USD'), (BTC, 'BTC'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=GBP)
    
    quantity = models.DecimalField(default=0, max_digits=20,decimal_places=4)
    price = models.DecimalField(default=0, max_digits=30, decimal_places=10)
    
    BUY = 'Buy'
    SELL = 'Sell'
    CONTRACT_CHOICES = ((BUY, 'BUY'),(SELL, 'SELL'))    
    contract_type = models.CharField(max_length=4, choices=CONTRACT_CHOICES, default=BUY)
    
    #location = models.CharField(max_length=8)
    #completion_date = models.DateField()
    
    def write(self):
        return '{' + '"buyer" : "{}", "seller" : "{}", "asset_name" : "{}", "unit" : "{}", "currency" : "{}", "quantity" : "{}", "price" : "{}"'.format(self.buyer, self.seller, self.asset_name, self.unit, self.currency, self.quantity, self.price) + '}'
        
    def boundsAsList(self):
        list = []
        for i in self.bounds.split("|"):
            list.append(i.split(","))
        return list
        
    
   
class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email','password']


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

# Additional class to store a user's wallet information
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_private_key = models.CharField(max_length=64)
    wallet_address = models.CharField(max_length=42)

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_wallet(sender, instance, **kwargs):
    instance.wallet.save()

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['wallet_private_key', 'wallet_address']
        
class OfferCreationForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['contract_type', 'asset_name', 'completion_condition', 'unit', 'currency']
        