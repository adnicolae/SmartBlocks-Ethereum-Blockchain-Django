from django.shortcuts import render, redirect
from django.forms import ModelForm
from webapp.models import RecordForm,Record,UserForm,WalletForm,OfferCreationForm,AssetCreationForm,SignupForm,Offer,Asset
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.urls import reverse
from urllib.parse import urlencode

from django.db.models import Q

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from .forms import ChangeUsernameForm, SearchOfferForm, SearchOfferFormAdvance

from django.forms.models import model_to_dict

from .matcher import match as matchBounds, parseString, strToListOfBounds

from webapp.solidity import SolidityHelper

from webapp.blockchain import sendContract

import json

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, defer


class SendBlockchainProtocol(Protocol):

    def sendContract(self, data):
        d = defer.Deferred()
        self.transport.write(data)
        return d

def sendJSON(p, data):
    d = p.sendContract(str.encode(data + '\r\n'))
    d.addCallback(lambda stop: reactor.stop())

def index(request):
    return render(request, 'webapp/index.html')
    

@login_required
def offers(request):
	buy_offers = Offer.objects.filter(seller=None).exclude(buyer=request.user)
	sell_offers = Offer.objects.filter(buyer=None).exclude(seller=request.user)
	eth_assets = Asset.objects.filter(stock__gt=0).exclude(owner=request.user)
	return render(request, 'webapp/offers.html', {'buy_offers':buy_offers,'sell_offers':sell_offers, 'eth_assets':eth_assets})

@login_required
def details(request, offer_id):
    if request.method == 'POST':
        pageOrigin = request.POST.get('pageOrigin')
    else:
        pageOrigin = None
    offer = Offer.objects.get(pk=offer_id)
    bounds = offer.bounds.split("|")
    for i in range(len(bounds)):
        bounds[i] = bounds[i].split(",")
    if(offer is None):
        return redirect('webapp:offers')
    return render(request, 'webapp/details.html', {'offer':offer, 'bounds':bounds,'pageOrigin':pageOrigin})


@login_required
def updateStatus(request, record_generated_id):
	user = User.objects.get(pk=request.user.id)
	record = Record.objects.get(generatedId=record_generated_id)

	previous_status = record.status

	if user.id == record.buyer.id and record.status == record.DELIVERED:
		record.status = record.CONFIRMED
	elif user.id == record.asset.carrier.id and record.status == record.TRANSIT:
		record.status = record.DELIVERED

	record.save()
	return render(request, 'webapp/status.html', {'record': record, 'previous_status': previous_status})

@login_required
def recordDetails(request, record_id):
	record = Record.objects.get(pk=record_id)
	if record is None:
		return redirect('webapp:myOffers')

	qr_code = SolidityHelper.generateQRCode(record.generatedId)

	return render(request, 'webapp/recordDetails.html', {'record': record, 'qr_code': qr_code})

@login_required
def assetDetails(request, asset_id):
	asset = Asset.objects.get(pk=asset_id)
	user = User.objects.get(pk=request.user.id)
	if(asset is None):
		return redirect('webapp:offers')
	if request.method == "POST":
		form = RecordForm(request.POST)
		if form.is_valid():
			record = form.save(commit=False)

			record.generatedId = str(SolidityHelper.generateId(user.username))[2:-1]
			record.asset = asset
			record.status = record.PROCESSING
			record.owed = record.amount * asset.price/2
			record.buyer = user
			print(record.buyer)
			print(asset.generatedId)
			print(record.amount)
			print(record.generatedId)
			print(int(asset.price/2))

			record.save()

			SolidityHelper.buy_asset(user.id, user.wallet.wallet_address, user.wallet.wallet_private_key, asset.generatedId, record.amount, record.generatedId, int(record.amount * asset.price/2))
			return redirect("webapp:myOffers")
	else:
		form = RecordForm()
	return render(request, 'webapp/assetDetails.html', {'asset': asset, 'form': form})

@login_required
def sign(request, offer_id):
    sign_contract(request, offer_id)

    return redirect('webapp:myOffers')

def sign_contract(request, offer_id, price=-1, quantity=-1):
    offer = Offer.objects.get(pk=offer_id)
    user = User.objects.get(pk=request.user.id)
    if(offer is None):
        return redirect('webapp:offers')
    if(offer.buyer is None and offer.seller is user):
        return redirect('webapp:offers')
    if(offer.seller is None and offer.buyer is user):
        return redirect('webapp:offers')
    
    offer.pk = None
    if quantity == -1:
        offer.stock = float(offer.stock) - float(request.POST.get('post_quantity'))
    else:
        offer.stock = float(offer.stock) - float(quantity)
    offer.save()
    
    old_offer = Offer.objects.get(pk=offer_id)
    if quantity == -1:
        old_offer.price = request.POST.get('post_price')
        old_offer.quantity = request.POST.get('post_quantity')
    else:
        old_offer.price = price
        old_offer.quantity = quantity
    if(old_offer.buyer is None):
        old_offer.buyer = user
    elif(old_offer.seller is None):
        old_offer.seller = user
        
    old_offer.save()
    
    d = old_offer.write()
    b = d.encode('utf-8')

    buyer_pr_key = RSA.import_key(old_offer.buyer.profile.private_key)

    seller_pr_key = RSA.import_key(old_offer.seller.profile.private_key)

    #encrypt d with buyer and seller private keys.
    cipher_buyer = PKCS1_OAEP.new(key=buyer_pr_key)
    cipher_text_buyer = cipher_buyer.encrypt(b)
    cipher_seller = PKCS1_OAEP.new(key=seller_pr_key)
    cipher_text_seller = cipher_seller.encrypt(b)
    
    d = d[:-1] + ', "cipher_buyer" : "{}", "cipher_seller" : "{}"'.format(cipher_text_buyer, cipher_text_seller) + '}'

    pu_key_buyer = RSA.import_key(old_offer.buyer.profile.public_key).exportKey()
    pu_key_seller = RSA.import_key(old_offer.seller.profile.public_key).exportKey()
    
    sendContract.send(d, pu_key_buyer, pu_key_seller, cipher_text_buyer, cipher_text_seller)

def login_view(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('email')
            password=form.cleaned_data.get('password')
            user = auth.authenticate(username=username,password=password)
            if(user is not None) :
                auth.login(request, user)
                toastHTML = '<span>Logged in successfully!</span>'
                messages.success(request, toastHTML)
                return redirect((request.GET.get('next','webapp:dashboard')))
    else:
        form = UserForm()
    return render(request, 'webapp/login.html', {'form': form})
    
def register(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            user.username = user.email
            
            user.save()            
            
            private_key = RSA.generate(2048)
            public_key = private_key.publickey()
            
            private_pem = private_key.export_key().decode()
            public_pem = public_key.export_key().decode()
            
            user.profile.private_key = public_pem
            user.profile.public_key = private_pem
            
            user.save()
            
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=user.username, password=raw_password)
            auth.login(request, user)
            toastHTML = '<span>Registered successfully!</span>'
            messages.success(request, toastHTML)
            return redirect('webapp:dashboard')
    else:
        form = SignupForm()
    return render(request, 'webapp/register.html', {'form': form})

def logout_view(request):
    auth.logout(request)
    toastHTML = '<span>Logged out successfully!</span>'
    messages.success(request, toastHTML)
    return redirect('webapp:index')

@login_required
def createAsset(request):
	if request.method == "POST":
		form = AssetCreationForm(request.POST)
		if form.is_valid():
			asset = form.save(commit = False)
			user = User.objects.get(id=request.user.id)
			carrier = User.objects.get(username='carrier@solidity.com')

			genid = SolidityHelper.generateId(asset.name)
			asset.owner = user
			asset.carrier = carrier
			asset.generatedId = str(genid)[2:-1]
			asset.transactionStatus = asset.SUBMITTED

			print("Asset name: ", asset.name)
			print("User wallet: ", user.wallet.wallet_address)
			print("Carrier wallet: ", carrier.wallet.wallet_address)
			print("Asset id: ", asset.generatedId)

			asset.save()

			SolidityHelper.create_asset(user.id, user.wallet.wallet_address, user.wallet.wallet_private_key, asset.generatedId, form.cleaned_data['name'], form.cleaned_data['description'],
										int(form.cleaned_data['price']), int(form.cleaned_data['stock']),
										form.cleaned_data['location'], form.cleaned_data['transferTime'],
										[asset.owner.wallet.wallet_address, asset.carrier.wallet.wallet_address],
										[90, 10])
			return redirect("webapp:myOffers")
	else:
		form = AssetCreationForm()
	return render(request, 'webapp/createAsset.html', {'form': form})

@login_required
def createOffer(request):
    if request.method == "POST":
        form = OfferCreationForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            user = User.objects.get(id=request.user.id)
        
            contract_str = ""
            if(request.POST.get("drag-and-drop-str","") is not None):
                print("drag and drop used")
                contract_str = request.POST.get("drag-and-drop-str","")
            else:
                print("text input used")
                contract_str = form.cleaned_data['completion_condition']
            
            offer.completion_condition = contract_str
                

            if form.cleaned_data.get('contract_type') == 'Sell' :
                offer.seller = user
                priority = 'seller'
            else:
                offer.buyer = user
                priority = 'buyer'
        
            clause = parseString(contract_str)
            if clause is None:
                form.add_error('completion_condition', 'Invalid clause')
                return render(request, 'webapp/createOffer.html', {'form': form})
            index = 0
            strBounds = ""
            for bounds in clause.bounds:
                if index >= 1 :
                    strBounds+="|"
                strBounds += "{},{},{},{}".format(str(bounds.pl), str(bounds.pu), str(bounds.ql), str(bounds.qu))
                index+=1
                
            offer.bounds = strBounds

            #try to find match
            if form.cleaned_data.get('contract_type') == 'Buy':
                potential_matches = Offer.objects.filter(contract_type='Sell',asset_name=offer.asset_name,buyer=None)
            else:
                potential_matches = Offer.objects.filter(contract_type='Buy',asset_name=offer.asset_name, seller=None)

            match_list = []
            for m in potential_matches:
                m_bounds = strToListOfBounds(m.bounds)
                out = matchBounds(clause.bounds, m_bounds, priority)
                if out is not None:
                    #contracts match
                    quant = min(offer.stock, m.stock)
                    quant = max(0, quant)
                    if quant == 0 :
                        continue
                    if len(match_list) == 0:
                        match_list.append((out, m.id))
                    elif priority is 'buyer':
                        index = 0
                        for match in match_list:                            
                            if (match[0][0] > out[0]) or (match[0][0] == out[0] and match[0][1] < quant): 
                                match_list.insert(index, ((out[0], quant), m.id))
                                break
                            index += 1
                        match_list.append((out, m.id))
                    else:
                        index = 0
                        for match in match_list:                            
                            if (match[0][0] < out[0]) or (match[0][0] == out[0] and match[0][1] < quant): 
                                match_list.insert(index, ((out[0], quant), m.id))
                                break
                            index += 1
                        match_list.append((out, m.id))
                    
            if len(match_list) > 0:
                toastHTML = '<span>A match was automatically found!</span>'
                messages.success(request, toastHTML)
                index = 0
                while(offer.stock > 0 and index < len(match_list)):
                    match = match_list[index]
                    print("matching with offer id {}, price {} quant {}".format(match[1], match[0][0], match[0][1]))
                    quant = min(offer.stock, match[0][1])
                    offer.stock = float(offer.stock) - quant
                    sign_contract(request, match[1], match[0][0], quant)
                    index += 1
           
            if(offer.stock > 0):
                offer.save()
                detailsURL = reverse('webapp:details', args=[offer.id])
                toastHTML = '<span>Offer created successfully!</span><a class="btn-flat toast-action waves-effect waves-light white-text" href="{}">View</a>'.format(detailsURL);
            
                messages.success(request, toastHTML)

            return redirect('webapp:myOffers')
    else:
        form = OfferCreationForm()
    return render(request, 'webapp/createOffer.html', {'form': form})

def changeOffer(request, offer_id):
	offer = Offer.objects.get(pk=offer_id)
	if request.method == 'POST':
		user = User.objects.get(pk=request.user.id)
		form = OfferCreationForm(request.POST,instance=offer)
		if form.is_valid():
			offer = form.save()
			toastHTML = '<span>Offer updated successfully!</span>'
			messages.success(request, toastHTML)
			return redirect('webapp:myOffers')
	else:
		form = OfferCreationForm(instance=offer)
	return render(request, 'webapp/changeOffer.html',{'form':form})

def deleteOffer(request, offer_id):
	offer = Offer.objects.get(pk=offer_id)
	offer.delete()
	toastHTML = '<span>Offer deleted successfully!</span>'
	messages.success(request, toastHTML)
	return redirect('webapp:myOffers')

@login_required
def myOffers(request):
	user = request.user
	buy_offers = Offer.objects.filter(buyer=user,seller=None)
	sell_offers = Offer.objects.filter(seller=user,buyer=None)
	completed_offers = Offer.objects.filter(Q(buyer=user) | Q(seller=user)).exclude(buyer=None).exclude(seller=None)
	assets = Asset.objects.filter(owner=user)
	records = Record.objects.filter(buyer=user)
	return render(request, 'webapp/myOffers.html', {'buy_offers':buy_offers,'sell_offers':sell_offers,'completed_offers':completed_offers, 'assets':assets, 'records':records})

@login_required
def myAssets(request):
	user = request.user
	assets = Asset.objects.filter(owner=user)
	records = Record.objects.filter(buyer=user)
	return render(request, 'webapp/myAssets.html', {'owned_assets': assets, 'records': records})

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

def searchOffers(request):
	if request.method == 'POST':
		form = SearchOfferForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['asset_name']
			quantity = form.cleaned_data['quantity']
			price = form.cleaned_data['price']
			contract_type = form.cleaned_data['contract_type']
			offers = []
			if contract_type == 'Buy':
				potential_matches = Offer.objects.filter(contract_type='Sell',asset_name=name, seller=None)
				priority = 'seller'
			else:
				potential_matches = Offer.objects.filter(contract_type='Buy',asset_name=name, buyer=None)
				priority = 'buyer'
			
			searchCondition = "p ="+ str(price) + "AND q =" + str(quantity)
			clause = parseString(searchCondition)
			for m in potential_matches:
				pot_mat_clause = parseString(m.completion_condition)
				out = matchBounds(clause.bounds, pot_mat_clause.bounds, priority)
				if out is not None:
					offers.append(m)
					
			# If not offers found
			if not offers:
				noMatch = 1
			else:
				noMatch = 0
		else:
			offers = None
			print("invalid form")
	else:
		form = SearchOfferForm()
		offers = None
		noMatch = 0
	return render(request,'webapp/searchOffers.html',{'form':form,'offers':offers,'noMatch':noMatch})
	
def searchOffersAdvanced(request):
	if request.method == 'POST':
		form = SearchOfferFormAdvance(request.POST)
		if form.is_valid():
			name = form.cleaned_data['asset_name']
			contract_type = form.cleaned_data['contract_type']
			offers = []
			if contract_type == 'Buy':
				potential_matches = Offer.objects.filter(contract_type='Sell',asset_name=name)
				priority = 'seller'
			else:
				potential_matches = Offer.objects.filter(contract_type='Buy',asset_name=name)
				priority = 'buyer'
			
			searchCondition = form.cleaned_data['completion_condition']
			clause = parseString(searchCondition)			
			for m in potential_matches:
				pot_mat_clause = parseString(m.completion_condition)
				out = matchBounds(clause.bounds, pot_mat_clause.bounds, priority)
				if out is not None:
					offers.append(m)
					
			# If not offers found
			if not offers:
				noMatch = 1
			else:
				noMatch = 0
		else:
			offers = None
			print("invalid form")
	else:
		form = SearchOfferFormAdvance()
		offers = None
		noMatch = 0
	return render(request, 'webapp/searchOffersAdvanced.html', {'form':form, 'offers':offers, 'noMatch':noMatch})
@login_required
def dashboard(request):
    return render(request, 'webapp/dashboard.html')

def about(request):
    return render(request, 'webapp/about.html')

@login_required
def changePassword(request):

	if request.method == 'POST':
		form = PasswordChangeForm(request.user,request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request,user)
			messages.success(request,'Your password was updated')
			return redirect('webapp:settings')
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
				return redirect('webapp:settings')
			else:
				messages.error(request,'Wrong Password')
		else:
			messages.error(request,'Error')
	else:
		form = ChangeUsernameForm()
	return render(request,'webapp/changeUsername.html',{'form':form})

@login_required
def changeWallet(request):
	if request.method == 'POST':
		form = WalletForm(request.POST, instance=request.user.wallet)
		if form.is_valid():
			wallet = form.save()
			wallet.ether_balance = SolidityHelper.getBalance(wallet.wallet_address)
			wallet.save()
			return redirect('webapp:dashboard')
		else:
			messages.error(request, "Wrong address.")
	else:
		form = WalletForm(instance = request.user.wallet)
	return render(request, 'webapp/changeWallet.html', {'form': form})

@login_required
def settings(request):
	return render(request, 'webapp/settings.html')

def contractsHub(request):
	return render(request, 'webapp/contractsHub.html')
