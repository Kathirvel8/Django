from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from .models import Cart, CartItem, Orders
from django.conf import settings
import requests
import paypalrestsdk

# Create your views here.
paypalrestsdk.configure({
	"mode":settings.PAYPAL_MODE, 
    "client_id": settings.PAYPAL_CLIENT_ID, 
	"client_secret": settings.PAYPAL_CLIENT_SECRET
	})

def get_products(categories):
	all_products = {}
	for category in categories:
		url = f"https://dummyjson.com/products/category/{category}"
		response = requests.get(url, verify=False)
		data = response.json()

		all_products[category] = data["products"]
	return all_products

def index(request):
	added_item_id = request.session.pop("added_item_id", None)
	categories = ['mens-shoes', 'womens-shoes']
	all_products = get_products(categories)
	show_text = True
	return render(request, 'index.html', {"all_products": all_products, 'show_text': show_text, "added_item_id": added_item_id})

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
	print("get", request.GET.get('next'))
	print("post", request.POST.get('next'))
	form = LoginForm()
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				auth_login(request, user)
				next_url = request.GET.get('next') or request.POST.get('next')
				print("next_url", next_url)
				if next_url:
					return redirect(next_url)
				else:
					return redirect("index")

	return render(request, "login.html", {'form': form})

def logout_user(request):
	logout(request)
	return redirect('index')

def get_user_cart(user):
	cart, created = Cart.objects.get_or_create(user=user)
	return cart

@login_required
def add_to_cart(request, item_id):
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
		request.session["added_item_id"] = item_id
		return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def cart(request, quantity=0, tax=0, price=0):
	cart = get_user_cart(user=request.user)
	items = cart.items.all()
	
	for item in items:
		item.total_item_price = round(item.price * item.quantity, 2)
		item.added_product_id = item.product_id
		price += item.total_item_price
		quantity += item.quantity
	ids = [int(item.added_product_id) for item in items]
	tax = round(0.05 * price, 2)
	total_price = round(tax + price, 2)
	categories = ['mens-shoes']
	products = get_products(categories)

	user_cart = Cart.objects.get(user_id=request.user.id)
	user_cart.total_amount = total_price
	user_cart.save()
	
	return render(request, 'cart.html', {'items': items, 'quantity': quantity, 'subtotal': price, 'tax': tax, 'total': total_price, "all_products": products, "ids": ids})

def remove_cart(request, item_id):
	cart = get_user_cart(request.user)
	item = CartItem.objects.get(cart=cart, id=item_id)
	if item.quantity > 1:
		item.quantity -= 1
		item.save()
	else:
		item.delete()
	return redirect('cart')

def add_cart_item(request, item_id):
	cart = get_user_cart(request.user)
	item = CartItem.objects.get(cart=cart, id=item_id)
	if item.quantity >=1:
		item.quantity += 1
		item.save()
	return redirect('cart')

def remove_cart_item(request, item_id):
	cart = get_user_cart(request.user)
	item = CartItem.objects.get(cart=cart, id=item_id)
	if request.user.is_authenticated:
		item.delete()
	return redirect('cart')

def checkout(request):
	cart = Cart.objects.get(user_id=request.user.id)
	total_price = cart.total_amount

	payment = paypalrestsdk.Payment({
		"intent": "sale",
		"payer": {
			'payment_method': 'paypal'
		},
		"redirect_urls": {
			"return_url": request.build_absolute_uri("/payment_success"),
			"cancel_url": request.build_absolute_uri("/cart"),
    	},
		"transactions": [{
			"amount":{ 
				"total": str(total_price),
				"currency": "USD"
			},
		}]
	})
	if payment.create():
		order = Orders.objects.create(user_id=request.user, total_amount=total_price, payment_id=payment.id)
		print("success")
		order.save()

		for link in payment.links:
			if link.rel == "approval_url":
				return redirect(link.href)
			
	return render(request, "error.html", {"error": payment.error})

def payment_success(request):
	payment_id = request.GET.get('paymentId')
	payer_id = request.GET.get("PayerID")

	order = Orders.objects.filter(payment_id=payment_id).first()
	payment = paypalrestsdk.Payment.find(payment_id)

	if not payer_id:
		return render(request, "error.html", {'error': 'Missing PayerID in PayPal response'})

	if payment.execute({"payer_id": payer_id}):
		order.is_paid = True
		order.save()

		return render(request, 'success.html')
	return render(request, "error.html", {'error': payment.error})