from django.urls import path
from . import views

# app_name = "shop"

urlpatterns = [
	path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("cart", views.cart, name="cart"),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_cart/<int:item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('add_cart/<int:item_id>/', views.add_cart_item, name='add_cart_item'),
    path('checkout', views.checkout, name="checkout"),
    path('payment_success', views.payment_success, name="payment_success"),
]