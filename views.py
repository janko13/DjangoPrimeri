from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product,Address,Comment,Basket,BasketList
from .forms import ProductForm, LoginForm, RegisterForm,UserForm,CommentForm,AddProductForm,SearchForm,OrderForm
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import sys

app_name = "The RockMix"
def index(request):
	"""The landing page
  
	This is the landing page of the app. It contains a slideshow of best selers
	(to change replace imagages slide1 and slide2 in static/rock). It has a top menu,
	login adn search bar.

	Keyword arguments:
	request -- the django requst object
	"""
  	context = {'loginForm':LoginForm(),'searchForm':SearchForm()}
  	context['invalid']=False
  	return render(request, 'rock/index.html', context)
  
def search(request):
	"""
	The search page
	
	This is where all the products all displayed, orderd by the date they were put into database,
	newest on top. It has top menu, login and search bar
	
	Keyword arguments:
	request -- the django requst object
	"""
	context = {'loginForm':LoginForm(),'searchForm':SearchForm()}
	order = request.GET.get('order','-pub_date')
	product_list = Product.objects.order_by(order)
	paginator = Paginator(product_list, 10)
   	page = request.GET.get('page')
   	try:
  	     products = paginator.page(page)
 	except PageNotAnInteger:
 	      products = paginator.page(1)
   	except EmptyPage:
   	    products = paginator.page(paginator.num_pages)
	context['products'] = products
	return render(request, 'rock/SearchPage.html', context)

def search_by(request):
	"""
	The search page
	
	Almost the same as search only that it shows products that matched search word
	
	Keyword arguments:
	request -- the django requst object
	"""
	context={'loginForm':LoginForm(),'searchForm':SearchForm()}
	context['products']=None
	if request.method=='POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			word = form.cleaned_data['search']
			product_list = Product.objects.annotate(search=SearchVector('title','artist','tracks')).filter(search=word)
			paginator = Paginator(product_list, 10)
			page = request.GET.get('page')
		   	try:
		  	     products = paginator.page(page)
		 	except PageNotAnInteger:
		 	      products = paginator.page(1)
		   	except EmptyPage:
		   	    products = paginator.page(paginator.num_pages)
			context['products'] = products
	return render(request, 'rock/SearchPage.html', context)

def product(request,product_id):
	"""
	The product page
	
	It displays basic information about product. If you are logged in then you can
	post comments and put prodcut in basket. If you have special privileges then you can also
	edit the product. It has top menu, login and search bar.
	
	Keyword arguments:
	request -- the django requst object
	product_id -- id of the displayed product
	"""
	context = {'loginForm':LoginForm(),'searchForm':SearchForm()}
	product = Product.objects.get(pk=product_id)
	context['commentForm'] = CommentForm()
	context['addProductForm'] = AddProductForm()
	context['product'] = product
	if request.method == 'POST':
		if request.POST.get('comment'):
			f = CommentForm(request.POST)
			if f.is_valid():
				text = request.POST.get('text','')
				comment = Comment.objects.create(owner = request.user,product = product,comment=text)
				return HttpResponseRedirect(reverse('product', args=[product_id]))#ne dela pravilno ne vrne tega drugace pa objavi v bazo
		elif request.POST.get('item'):
			f = AddProductForm(request.POST)
			if f.is_valid():
				number = f.cleaned_data['number']
				basket = Basket.objects.filter(owner = request.user).order_by('-pub_date')
				if not basket or not basket[0].not_orderd():
					basket = Basket.objects.create(owner = request.user)
					basket.save()
					basketList = BasketList.objects.create(basket = basket, product = product,quantity=number)
					return HttpResponseRedirect(reverse('product', args=[product_id]))
				elif basket[0].not_orderd() and basket[0].is_valid():
					basketList=BasketList.objects.filter(basket=basket[0],product=product)
					if not basketList:
						basketList = BasketList.objects.create(basket = basket[0], product = product,quantity=number)
						basketList.save()
					return HttpResponseRedirect(reverse('product', args=[product_id]))
				elif basket[0].not_orderd():
					basket[0].delete()
					basket = Basket.objects.create(owner = request.user)
					basket.save()
					basketList = BasketList.objects.create(basket = basket, product = product,quantity=number)
					
				#productList = BasketList.objects.create(
	context['list'] = context['product'].tracks.split(';')
	context['comments'] = Comment.objects.filter(product=product_id).order_by('-pub_date');
	return render(request, 'rock/ProductPage.html', context)
  
def contact(request):
	"""
	The contact page
	
	It shows basic informations about company. It has top menu, login and search bar
	
	Keyword arguments:
	request -- the django requst object
	"""
	context = {'loginForm':LoginForm(),'searchForm':SearchForm()}
	return render(request, 'rock/ContactPage.html', context)

@login_required	
def basket(request):
	"""
	The basket page
	
	It displayes products, that are currently in the basket(if any) and old orders.
	It has top menu and search bar.
	
	Keyword arguments:
	request -- the django requst object
	"""
	
	context = {'products':None,'searchForm':SearchForm()}
	context['not_orderd_basket'] = None
	context['sum'] = 0
	basket = Basket.objects.filter(owner = request.user).order_by('-pub_date')
	if not basket:
		print("Ni kosaric")
	elif basket[0].not_orderd() and basket[0].pub_date.date() != datetime.now().date():
		basket[0].delete()
		context['baskets']=basket
	elif basket[0].not_orderd():
		context['not_orderd_basket'] = basket[0]
		basketList = BasketList.objects.filter(basket = basket[0])
		for product in basketList:
			context['sum'] += product.quantity*product.product.price
		context['products'] = basketList
	context['baskets']=Basket.objects.filter(owner = request.user,isOrderd=1).order_by('-pub_date')
	list_of_baskets=[]
	for basket in context['baskets']:
		list_of_baskets.append(BasketList.objects.filter(basket=basket))	
	context['list_of_baskets'] = list_of_baskets
	return render(request, 'rock/BasketPage.html', context)

def register(request):
	"""
	The register page
	
	It alaws new user to register, by filing their personal informations.
	It has top menu and login.
	
	Keyword arguments:
	request -- the django requst object
	"""
	context = {'loginForm':LoginForm()}
	rform = RegisterForm()
	uform = UserForm()
	if request.method == 'POST':
		rform = RegisterForm(request.POST)
		uform = UserForm(request.POST)
		if rform.is_valid() and uform.is_valid():
			passw = uform.cleaned_data['password']
			user = uform.cleaned_data['username']
			mail = uform.cleaned_data['email']
			firstName = uform.cleaned_data['first_name']
			lastName = uform.cleaned_data['last_name']
			u = User.objects.create_user(username=user,password=passw,email=mail,first_name=firstName,last_name=lastName,is_superuser='f',is_staff='f',is_active='t')
			u.save()
			naslov = rform.cleaned_data['address']
			kraj = rform.cleaned_data['city']
			posta = rform.cleaned_data['zipcode']
			a = Address.objects.create(user = u,address=naslov,city=kraj,zipcode=posta)
			a.save()
			return HttpResponseRedirect(reverse('index'))	
	context['registerForm'] = rform
	context['userForm'] = uform
	return render(request, 'rock/RegisterPage.html', context)
	
def reset(request):
	"""
	The reset page
	
	By giving your register email, email with link to reset password will be sent(it doesnt work yet).
	
	Keyword arguments:
	request -- the django requst object
	"""
	context = {'loginForm':LoginForm(),'searchForm':SearchForm()}
	return render(request, 'rock/PasswordResetPage.html', context)

@permission_required('rock.Can_add_product')
def add(request):
	"""
	The product add page
	
	It displays a form for creating new product.
	It has top menu and search bar.
	
	Keyword arguments:
	request -- the django requst object
	"""
	context = {'searchForm':SearchForm()}
	pform = ProductForm()
	if request.method=='POST':
		if request.POST.get('save'):
			pform = ProductForm(request.POST)
			if pform.is_valid():
			  	pform.save()
			  	return HttpResponseRedirect(reverse('add'))
		else:
			return HttpResponseRedirect(reverse('add'))
	context['productForm'] = pform
	return render(request, 'rock/AddProduct.html', context)

@permission_required('rock.Can_change_product')
def change(request,product_id):
	"""
	The change product page
	
	It display form field with product informations that can be changed and saved.
	It has top menu and search bar.
	
	Keyword arguments:
	request -- the django requst object
	product_id -- id of the product
	"""
	context = {'searchForm':SearchForm()}
	product = Product.objects.get(pk=product_id)
	pform = ProductForm(instance=product)
	if request.method=='POST':
		if request.POST.get('delete'):
			product.delete()
			return HttpResponseRedirect(reverse('add'))
		else:
			pform = ProductForm(request.POST, instance=product)
			if pform.is_valid():
			  	pform.save()
			  	return HttpResponseRedirect(reverse('add'))		
	context['productForm'] = pform
	return render(request, 'rock/AddProduct.html', context)

@login_required
def checkout(request,basket_id):
	"""
	The checkout page
	
	It display information about current basket(it has not been yet orderd) and alows to change it.
	
	Keyword arguments:
	request -- the django requst object
	basket_id -- id of the basket
	"""
	context = {'searchForm':SearchForm()}
	basket=Basket.objects.get(pk=basket_id)
	context['basket'] = basket
	basketList = BasketList.objects.filter(basket=basket)
	list_of_items=[]
	for item in basketList:
		list_of_items.append(OrderForm(initial={'name': item.product.title+" "+item.product.artist,'cost':item.product.price,'quantity':item.quantity,'check':item.id}))
	context['orderForms']=list_of_items
	if request.method=='POST':
		if request.POST.get('remove'):
			checks = request.POST.getlist('check')
			for value in checks:
				delete = BasketList.objects.get(pk=value)
				delete.delete()
			return HttpResponseRedirect(reverse('checkout',args=[basket_id]))
		elif request.POST.get('change'):
			numbers = request.POST.getlist('quantity')
			i = 0
			while i<len(numbers):
				basketList[i].quantity = numbers[i]
				basketList[i].save()
				i += 1
			return HttpResponseRedirect(reverse('summery',args=[basket_id]))
	return render(request, 'rock/CheckOutPage.html', context)

@login_required
def summery(request,basket_id):
	"""
	The last page before submiting order
	
	Summery of information about products we are ordering and user information.
	
	Keyword arguments:
	request -- the django requst object
	basket_id -- id of the basket
	"""
	context = {'searchForm':SearchForm()}
	basket=Basket.objects.get(pk=basket_id)
	context['basket']=basket
	basketList=BasketList.objects.filter(basket=basket)
	context['items']=basketList
	address=Address.objects.get(user=request.user)
	context['address']=address
	if request.method=='POST':
		basket.isOrderd=1
		basket.save()
		return HttpResponseRedirect(reverse('index')) 
	return render(request, 'rock/Summery.html', context)

def prijava(request):
	"""
	The login page
	
	It logs in user and redirects him to homepage.
	
	Keyword arguments:
	request -- the django requst object
	"""
	context = {'loginForm':LoginForm(),'searchForm':SearchForm()}
	if request.method=='POST':
		form = LoginForm(request.POST)
		if form.is_valid():
		  user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
		  if user is not None:
			login(request, user)
			context['invalid']=False
		  else:
		 	context['invalid']=True
			#return render(request,'rock/index.html', message='Neuspesna prijava')
	return render(request, 'rock/index.html', context)
	
def logout_user(request):
	"""
	The logout page
	
	It logs user out and redirects to homepage	
	
	Keyword arguments:
	request -- the django requst object
	"""
  	logout(request)
  	return HttpResponseRedirect(reverse('index'))
	
