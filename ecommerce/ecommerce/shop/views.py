from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
import requests

# Create your views here.

def index(request):
	categories = ['mens-shoes', 'womens-shoes']
	all_products = {}
	for category in categories:
		url = f"https://dummyjson.com/products/category/{category}"
		response = requests.get(url, verify=False)
		data = response.json()

		all_products[category] = data["products"]
	return render(request, 'index.html', {"all_products": all_products})

def register(request):
	form = RegisterForm()
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(form.cleaned_data['password'])
			user.save()
			messages.success(request, message="Registration successful")
			return redirect("/login")
	return render(request, 'register.html', {'form': form})

def login(request):
	form = LoginForm()
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				auth_login(request, user)
				print("success")
				return redirect("index")

	return render(request, "login.html", {'form': form})

def get_user_cart(user):
	cart, created = Cart.objects.get_or_create(user=user)
	return cart

@login_required
def add_to_cart(request):
	print("add to cart")
	print(request.POST)
	if request.method == 'POST':
		cart = get_user_cart(request.user)
		item, created = CartItem.objects.get_or_create(
			cart=cart,
			product_id=request.POST['id'],
			defaults={
				'title': request.POST['title'],
				'price': float(request.POST['price']),
				'discount': float(request.POST['discount']),
				'thumbnail': request.POST.get('thumbnail'),
			})
		if not created:
			item.quantity += 1
		item.save()
		return redirect('cart')

@login_required
def cart(request):
	cart = get_user_cart(user=request.user)
	items = cart.items.all()
	return render(request, 'cart.html', {'items': items})
