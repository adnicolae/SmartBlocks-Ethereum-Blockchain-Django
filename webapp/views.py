from django.shortcuts import render, redirect
from django.forms import ModelForm
from webapp.models import UserForm,OfferCreationForm,SignupForm,Offer
from webapp.backend import MyBackend
from django.contrib import auth

from django.db.models import Q

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'webapp/index.html')
    
def offers(request):
    all_offers = Offer.objects.all()
    return render(request, 'webapp/offers.html', {'all_offers':all_offers})
    
def details(request):
    return render(request, 'webapp/details.html')
    
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
    my_offers = [Offer.objects.get(Q(buyer=user) | Q(seller=user))]
    return render(request, 'webapp/myOffers.html', {'my_offers':my_offers})

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