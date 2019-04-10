from django.urls import path

from . import views

app_name='webapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('offers/', views.offers, name='offers'),
    path('details/<int:offer_id>', views.details, name='details'),
    path('assetDetails/<int:asset_id>', views.assetDetails, name='assetDetails'),
    path('recordDetails/<int:record_id>', views.recordDetails, name='recordDetails'),
    path('status/<str:record_generated_id>', views.updateStatus, name='status'),
    path('sign/<int:offer_id>', views.sign, name='sign'),
    path('createOffer/', views.createOffer, name='createOffer'),
    path('createAsset/', views.createAsset, name='createAsset'),
    path('myOffers/', views.myOffers, name='myOffers'),
    path('myAssets/', views.myAssets, name='myAssets'),
    path('mySmartBlocks/', views.mySmartBlocks, name='mySmartBlocks'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),    
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
	path('accountSetting/', views.accountSetting, name='accountSetting'),
	path('changePassword/', views.changePassword, name='changePassword'),
	path('changeUsername/', views.changeUsername, name='changeUsername'),
    path('changeWallet/', views.changeWallet, name='changeWallet'),
	path('changeOffer/<int:offer_id>', views.changeOffer, name='changeOffer'),
	path('deleteOffer/<int:offer_id>', views.deleteOffer, name='deleteOffer'),
	path('searchOffer/', views.searchOffer, name='searchOffer'),
	path('searchOfferAdvance/', views.searchOfferAdvance, name='searchOfferAdvance')
]