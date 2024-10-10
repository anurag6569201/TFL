from django.urls import path
from home import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/', views.add_to_cart, name='add_to_cart'),
]
