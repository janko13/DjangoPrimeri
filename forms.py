from django import forms
from .models import Product,Address
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class LoginForm(forms.Form):
	"""
	The LoginForm class\n
	LoginForm is used to get username and password from user for logging him into the system.
	"""
	username = forms.CharField(label=_('Uporabnisko ime'), max_length=48)
	password = forms.CharField(label=_('Geslo'),max_length=48, widget=forms.PasswordInput)


class ProductForm(forms.ModelForm):
	"""
	The ProductForm class\n
	It is used to for submiting a new product or updating an existing one
	"""
	title = forms.CharField(label=_('Naslov albuma'), max_length=48)
	artist = forms.CharField(label=_('Izvajalec'), max_length=48)
	price = forms.DecimalField(label=_('Cena'),max_digits=5, decimal_places=2)
	stock = forms.IntegerField(label=_('Zaloga'),initial=0)
	tracks = forms.CharField(label=_('Skladbe'),widget=forms.Textarea)
	year = forms.IntegerField(label=_('Leto izdaje'))
	#img = forms.ImageField(label=_('Slika'), required = False)
	kind = forms.CharField(label=_('Vrsta'),max_length=1)
	
	class Meta:
		model = Product
		fields = ['title','artist','price','stock','tracks','year','kind','genre']
		
class RegisterForm(forms.ModelForm):
	"""
	The RegisterForm class\n
	It is used, when new user register, to obtein their information about shipping address
	"""
	address = forms.CharField(label=_('Naslov'),max_length=48)
	city = forms.CharField(label=_('Kraj'),max_length=48)
	zipcode = forms.IntegerField(label=_('Postna stevilka'))
	class Meta:
		model = Address
		fields = ['address','zipcode','city']
		
class UserForm(forms.ModelForm):
	"""
	The UserForm class\n
	It is used to submit personal inforamtion about a user and also username and password
	"""
	first_name = forms.CharField(label=_('Ime'),max_length=48)
	last_name = forms.CharField(label=_('Priimek'),max_length=48)
	password = forms.CharField(label=_('Geslo'),max_length=48, widget=forms.PasswordInput)
	username = forms.CharField(label=_('Uporabnisko ime'),max_length=48)
	
	class Meta:
		model = User
		fields = ['first_name','last_name','email','username','password']
		
class CommentForm(forms.Form):
	"""
	The CommentForm\n
	It is used for comment submition about a product
	"""
	text = forms.CharField(label=_('Komentar'),widget=forms.Textarea)

class AddProductForm(forms.Form):
	"""
	The AddProductForm\n
	It is used to submit number of poducts user is ordering
	"""
	number = forms.IntegerField(label=_('Kolicina'),max_value=99, min_value=1,initial=1)
	
class SearchForm(forms.Form):
	"""
	The SearchForm\n
	It is used to obtein search parameters
	"""
	search = forms.CharField(label = "",max_length=64,widget=forms.TextInput(attrs={'placeholder': _('Vnesite iskalni niz..'),'type':'search'}))
	
class OrderForm(forms.Form):
	"""
	The OrderForm\n
	It is used for getting the last changes before submiting a order
	"""
	check=forms.BooleanField(label='',required = False)
	name=forms.CharField(label='',max_length=128,widget=forms.TextInput(attrs={'readonly':'readonly'}))
	cost=forms.IntegerField(label='',widget=forms.TextInput(attrs={'readonly':'readonly'}))
	quantity=forms.IntegerField(label='')
