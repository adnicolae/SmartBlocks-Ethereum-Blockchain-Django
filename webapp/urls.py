from django.urls import path

from . import views

app_name='webapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('offers/', views.offers, name='offers'),
    path('details/<int:offer_id>', views.details, name='details'),
    path('sign/<int:offer_id>', views.sign, name='sign'),
    path('createOffer/', views.createOffer, name='createOffer'),
    path('myOffers/', views.myOffers, name='myOffers'),
    path('mySmartBlocks/', views.mySmartBlocks, name='mySmartBlocks'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),    
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
	path('accountSetting/', views.accountSetting, name='accountSetting'),
	path('changePassword/', views.changePassword, name='changePassword'),
	path('changeUsername/', views.changeUsername, name='changeUsername'),
	path('changeOffer/<int:offer_id>', views.changeOffer, name='changeOffer'),
	path('searchOffer/', views.searchOffer, name='searchOffer')
]