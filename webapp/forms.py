from django import forms

class ChangeUsernameForm(forms.Form):
	newusername = forms.CharField(label='New Username', max_length=100)
	password = forms.CharField(widget=forms.PasswordInput)
	
class SearchOfferForm(forms.Form):
    asset_name = forms.CharField(max_length=100)
    quantity = forms.DecimalField( max_digits=20,decimal_places=4)
    price = forms.DecimalField(max_digits=30, decimal_places=10)
    CONTRACT_CHOICES = (('Buy', 'Buy'),('Sell', 'Sell'))    
    contract_type = forms.ChoiceField(choices=CONTRACT_CHOICES)