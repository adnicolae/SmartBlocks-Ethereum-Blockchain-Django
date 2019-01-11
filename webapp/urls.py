from django.urls import path

from . import views

app_name='webapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('offers/', views.offers, name='offers'),
    path('<int:offer_id/details/>', views.details, name='details'),
    path('createOffer/', views.createOffer, name='createOffer'),
    path('myOffers/', views.myOffers, name='myOffers'),
    path('mySmartBlocks/', views.mySmartBlocks, name='mySmartBlocks'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),    
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
]