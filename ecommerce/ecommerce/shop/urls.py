from django.urls import path
from . import views

# app_name = "shop"

urlpatterns = [
	path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("cart", views.cart, name="cart"),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
]