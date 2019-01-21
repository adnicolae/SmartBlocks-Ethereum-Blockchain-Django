from django import forms

class ChangeUsernameForm(forms.Form):
	newusername = forms.CharField(label='New Username', max_length=100)
	password = forms.CharField(widget=forms.PasswordInput)