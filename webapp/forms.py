from django import forms

class ChangeUsernameForm(forms.Form):
	newusername = forms.CharField(label='New Username', max_length=100)
	password = forms.CharField(widget=forms.PasswordInput)
	
class SearchOfferForm(forms.Form):
	asset_name = forms.CharField(max_length=100)
	quantity = forms.DecimalField( max_digits=20,decimal_places=4)
	price = forms.DecimalField(max_digits=30, decimal_places=10)
	#completion_condition = forms.CharField(max_length=256)
	CONTRACT_CHOICES = (('Buy', 'Buy'),('Sell', 'Sell'))    
	contract_type = forms.ChoiceField(choices=CONTRACT_CHOICES)
	
class SearchOfferFormAdvance(forms.Form):
	asset_name = forms.CharField(max_length=100)
	condition_help = "Keywords: <span class='keyword'>AND</span>, <span class='keyword'>OR</span>.</br>Operations: <, >, =</br>Variables: <span class='variable'>price</span>, <span class='variable'>quantity</span></br>Use parentheses to group statements.</br></br>Example:</br> (<span class='variable'>price</span> < 100 <span class='keyword'>AND</span> (<span class='variable'>quantity</span> > 20 <span class='keyword'>AND</span> <span class='variable'>quantity</span> < 50)) </br><span class='keyword'>OR</span> (<span class='variable'>price</span> < 120 <span class='keyword'>AND</span> <span class='variable'>quantity</span> < 20)<br>"
	completion_condition = forms.CharField(max_length=256, help_text=condition_help)
	CONTRACT_CHOICES = (('Buy', 'Buy'),('Sell', 'Sell'))    
	contract_type = forms.ChoiceField(choices=CONTRACT_CHOICES)