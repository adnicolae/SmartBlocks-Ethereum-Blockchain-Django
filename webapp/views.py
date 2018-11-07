from django.shortcuts import render


def index(request):
    return render(request, 'webapp/index.html')
    
def offers(request):
    return render(request, 'webapp/offers.html')
    
def details(request):
    return render(request, 'webapp/details.html')
    
def createOffer(request):
    return render(request, 'webapp/createOffer.html')
    