from django.shortcuts import render, redirect
from django.forms import ModelForm
from webapp.models import UserForm,OfferCreationForm,SignupForm,Offer
from webapp.backend import MyBackend
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.db.models import Q

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'webapp/index.html')
    
@login_required
def offers(request):
    buy_offers = Offer.objects.filter(seller=None).exclude(buyer=request.user)
    sell_offers = Offer.objects.filter(buyer=None).exclude(seller=request.user)
    return render(request, 'webapp/offers.html', {'buy_offers':buy_offers,'sell_offers':sell_offers})
    
@login_required
def details(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    if(offer is None):
        return redirect('webapp:offers')
    return render(request, 'webapp/details.html', {'offer':offer})
    
@login_required
def sign(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    user = User.objects.get(pk=request.user.id)
    if(offer is None):
        return redirect('webapp:offers')
    if(offer.buyer is None):
        offer.buyer = user
    elif(offer.seller is None):
        offer.seller = user
    offer.save()
    return redirect('webapp:myOffers')
    
def login_view(request):
    form = UserForm(request.POST)
    if form.is_valid():
        username=form.cleaned_data.get('email')
        password=form.cleaned_data.get('password')
        user = auth.authenticate(username=username,password=password)
        if(user is not None) :
            auth.login(request, user)
            return redirect('webapp:mySmartBlocks')
        else:
            form = UserForm()
    return render(request, 'webapp/login.html', {'form': form})
   
def logout_view(request):
    auth.logout(request)
    return redirect('webapp:index')
    
@login_required   
def createOffer(request):
    form = OfferCreationForm(request.POST)
    if form.is_valid():
        offer = form.save(commit=False)
        user = User.objects.get(id=request.user.id)
        
        if form.cleaned_data.get('contract_type') is 'SELL' :
            offer.seller = user
        else:
            offer.buyer = user
        
        offer.location = 'CV47AL'
        offer.save()
        
        return redirect('webapp:myOffers')
    return render(request, 'webapp/createOffer.html', {'form': form})

@login_required
def myOffers(request):
    user = request.user
    buy_offers = Offer.objects.filter(buyer=user)
    sell_offers = Offer.objects.filter(seller=user)
    return render(request, 'webapp/myOffers.html', {'buy_offers':buy_offers,'sell_offers':sell_offers})

@login_required
def mySmartBlocks(request):
    return render(request, 'webapp/mySmartBlocks.html')
    
def about(request):
    return render(request, 'webapp/about.html')
    
def register(request):
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save()
        user.email = user.username
        raw_password = form.cleaned_data.get('password1')
        user = auth.authenticate(username=user.username, password=raw_password)
        auth.login(request, user)
        return redirect('webapp:mySmartBlocks')        
    return render(request, 'webapp/register.html', {'form': form})
	
@login_required
def changePassword(request):
	form = PasswordChangeForm(request.user,request.POST)
	if form.is_valid():
		user = form.save()
		update_session_auth_hash(request,user)
		messages.success(request,'Your password was updated')
		return redirect('webapp:accountSetting')
	else:
		messages.error(request,'Error')
	
	return render(request, 'webapp/changePassword.html',{'form':form})
	
@login_required
def accountSetting(request):
	return render(request, 'webapp/accountSetting.html')