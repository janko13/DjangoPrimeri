from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.
class Genre(models.Model):
	"""
	Class Genre
	
	Object Genre with field genre, for storing product's genres
	"""
	genre = models.CharField(max_length = 48, null = False)
	def __str__(self):
	    return self.genre

class Product(models.Model):
	"""
	Class Product
	
	Here are stored all informations about a product
	"""
	title = models.CharField(max_length = 48, null = False)
	artist = models.CharField(max_length = 48, null = False)
	price = models.DecimalField(null=False, max_digits=5, decimal_places=2)
	stock = models.IntegerField(null = False, default = 0)
	tracks = models.TextField()
	year = models.IntegerField(null = False)
	#img = models.ImageField(upload_to='covers/',null=True)
	kind = models.CharField(max_length=1, null = False)
	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
	pub_date = models.DateTimeField( default=datetime.now )
	
	def __str__(self):
		return self.title
	
class Address(models.Model):
	"""
	Class Address
	
	Holds information about address of user
	"""
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	address = models.CharField(max_length = 48, null = False)
	zipcode = models.IntegerField(null = False)
	city = models.CharField(max_length = 48, null = False)
	
	def __str__(self):
		return self.address

class Comment(models.Model):
	"""
	Class Comment
	
	Holds information about who commented, what he commented and on which product
	"""
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
	comment = models.TextField()
  	pub_date = models.DateTimeField('date published', default=datetime.now )
  	
class Basket(models.Model):
	"""
	Class Basket
	
	Hold information about owner of the basket, when it was created and if it is alredy submited
	"""
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	isOrderd = models.IntegerField(null = True)
	pub_date = models.DateTimeField( default=datetime.now )
	
	def not_orderd(self):
		"""
		Function returns true if basket hasn't been yet submited
		"""
		if self.isOrderd == None:
			return True
		else: 
			return False
	def is_valid(self):
		if self.pub_date.date() == datetime.now().date():
			return True
		else:
			return False
	
class BasketList(models.Model):
	"""
	Class BasketList
	
	Holds information which product belongs to which basket and how many
	"""
	basket = models.ForeignKey(Basket, on_delete=models.CASCADE, null = False)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null = False)
	quantity = models.IntegerField(null = False,default=1)
	
	def whole_price(self):
		"""
		Function return price multiplied by quantity
		"""
		return self.product.price*self.quantity

