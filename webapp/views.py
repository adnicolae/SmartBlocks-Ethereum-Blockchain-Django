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

from .forms import ChangeUsernameForm, SearchOfferForm

from django.forms.models import model_to_dict

from .matcher import checkMatch

import json

from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor

class SendBlockchainProtocol(Protocol):
    def sendContract(self, data):
        self.transport.write(data)

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

        if form.cleaned_data.get('contract_type') == 'Sell' :
            offer.seller = user
            priority = 'seller'
        else:
            offer.buyer = user
            priority = 'buyer'

        offer.location = 'CV47AL'

        #try to find match
        if form.cleaned_data.get('contract_type') == 'Buy':
            potential_matches = Offer.objects.filter(contract_type='Sell',asset_name=offer.asset_name)
        else:
            potential_matches = Offer.objects.filter(contract_type='Buy',asset_name=offer.asset_name)

        for m in potential_matches:
            if checkMatch(offer.completion_condition, m.completion_condition, priority) is not None:
                #match found, calculate price and quantity to trade at
                offer.price, offer.quantity = checkMatch(offer.completion_condition, m.completion_condition, priority)
                if priority == 'buyer':
                    offer.seller = m.seller
                else:
                    offer.buyer = m.buyer

                #creates json serialisation to send to blockchain
                d = json.loads(offer.write())
                # e.g. blockchain.add(d) goes here
                #will also need to add this to

                break

        offer.save()

        return redirect('webapp:myOffers')
    return render(request, 'webapp/createOffer.html', {'form': form})

def changeOffer(request, offer_id):
	offer = Offer.objects.get(pk=offer_id)
	if request.method == 'POST':
		user = User.objects.get(pk=request.user.id)
		form = OfferCreationForm(request.POST,instance=offer)
		if form.is_valid():
			offer = form.save()
	else:
		form = OfferCreationForm(instance=offer)
	return render(request, 'webapp/changeOffer.html',{'form':form})

@login_required
def myOffers(request):
    user = request.user
    buy_offers = Offer.objects.filter(buyer=user,seller=None)
    sell_offers = Offer.objects.filter(seller=user,buyer=None)
    completed_offers = Offer.objects.filter(Q(buyer=user) | Q(seller=user)).exclude(buyer=None).exclude(seller=None)
    return render(request, 'webapp/myOffers.html', {'buy_offers':buy_offers,'sell_offers':sell_offers,'completed_offers':completed_offers})

@login_required
def matchOffer(request, offer_id):
	user = request.user

	myoffer = Offer.objects.get(pk=offer_id)
	#print(myoffer.contract_type)
	#TODO prevent buying your own stuff
	if myoffer.contract_type == 'Buy':
		offers = Offer.objects.filter(contract_type='Sell',asset_name=myoffer.asset_name)
	else:
		offers = Offer.objects.filter(contract_type='Buy',asset_name=myoffer.asset_name)
	sortedoffers = sorted(offers,key = lambda x: min(myoffer.quantity,x.quantity)/max(myoffer.quantity,x.quantity) + min(myoffer.price/myoffer.quantity,x.price/x.quantity)/max(myoffer.price/myoffer.quantity,x.price/x.quantity),reverse = True)[:10]
	return render(request,'webapp/matchOffer.html',{'sortedoffers':sortedoffers,'myoffer':myoffer})

def searchOffer(request):
	if request.POST.get('offer_id'):
		offer_id = request.POST.get('offer_id')
		myoffer = Offer.objects.get(pk=offer_id)
		form = SearchOfferForm({'asset_name':myoffer.asset_name,'quantity':myoffer.quantity,'price':myoffer.price,'contract_type':myoffer.contract_type})
		name = myoffer.asset_name
		quantity = myoffer.quantity
		price = myoffer.price
		contract_type = myoffer.contract_type
		if contract_type == 'Buy':
			offers = Offer.objects.filter(contract_type='Sell',asset_name=name)
		else:
			offers = Offer.objects.filter(contract_type='Buy',asset_name=name)
		sortedoffers = sorted(offers,key = lambda x: min(quantity,x.quantity)/max(quantity,x.quantity) + min(price/quantity,x.price/x.quantity)/max(price/quantity,x.price/x.quantity),reverse = True)[:10]
	elif request.method == 'POST':
		form = SearchOfferForm(request.POST)

		if form.is_valid():
			#print('hi')
			name = form.cleaned_data['asset_name']
			quantity = form.cleaned_data['quantity']
			price = form.cleaned_data['price']
			contract_type = form.cleaned_data['contract_type']
			if contract_type == 'Buy':
				offers = Offer.objects.filter(contract_type='Sell',asset_name=name)
			else:
				offers = Offer.objects.filter(contract_type='Buy',asset_name=name)
			sortedoffers = sorted(offers,key = lambda x: min(quantity,x.quantity)/max(quantity,x.quantity) + min(price/quantity,x.price/x.quantity)/max(price/quantity,x.price/x.quantity),reverse = True)[:10]
		else:
			sortedoffers = None
	else:
		form = SearchOfferForm()
		sortedoffers = None
	return render(request,'webapp/searchOffer.html',{'form':form,'sortedoffers':sortedoffers})
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

	if request.method == 'POST':
		form = PasswordChangeForm(request.user,request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request,user)
			messages.success(request,'Your password was updated')
			return redirect('webapp:accountSetting')
		else:
			messages.error(request,'Error')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'webapp/changePassword.html',{'form':form})

@login_required
def changeUsername(request):
	if request.method == 'POST':
		form = ChangeUsernameForm(request.POST)
		if form.is_valid():
			passw = form.cleaned_data['password']
			user = request.user
			if user.check_password(passw):
				newusername = form.cleaned_data['newusername']
				user.username = newusername
				user.save()
				return redirect('webapp:accountSetting')
			else:
				messages.error(request,'Wrong Password')
		else:
			messages.error(request,'Error')
	else:
		form = ChangeUsernameForm()
	return render(request,'webapp/changeUsername.html',{'form':form})

@login_required
def accountSetting(request):
	return render(request, 'webapp/accountSetting.html')
