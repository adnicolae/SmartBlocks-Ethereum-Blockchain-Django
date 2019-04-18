from django.urls import path

from . import views

app_name='webapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('offers/', views.offers, name='offers'),
    path('offers/<int:offer_id>', views.details, name='details'),
    path('assets/<int:asset_id>', views.assetDetails, name='assetDetails'),
    path('records/<int:record_id>', views.recordDetails, name='recordDetails'),
    path('status/<str:record_generated_id>', views.updateStatus, name='status'),
    path('sign/<int:offer_id>', views.sign, name='sign'),
    path('offers/create/', views.createOffer, name='createOffer'),
    path('assets/create/', views.createAsset, name='createAsset'),
    path('my-offers/', views.myOffers, name='myOffers'),
    path('my-assets/', views.myAssets, name='myAssets'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),    
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
	path('settings/', views.settings, name='settings'),
	path('settings/change-password/', views.changePassword, name='changePassword'),
	path('settings/change-username/', views.changeUsername, name='changeUsername'),
    path('settings/change-wallet/', views.changeWallet, name='changeWallet'),
	path('offers/change/<int:offer_id>', views.changeOffer, name='changeOffer'),
	path('offers/delete/<int:offer_id>', views.deleteOffer, name='deleteOffer'),
	path('search-simple/', views.searchOffers, name='searchOffers'),
	path('search-advanced/', views.searchOffersAdvanced, name='searchOffersAdvanced'),
	path('contracts/',views.contractsHub, name ='contractsHub' )
]