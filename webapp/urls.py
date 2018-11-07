from django.urls import path

from . import views

app_name='webapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('offers/', views.offers, name='offers'),
    path('<int:offer_id/details/>', views.details, name='details'),
    path('createOffer/', views.createOffer, name='createOffer'),
]