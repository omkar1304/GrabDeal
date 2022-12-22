from doctest import BLANKLINE_MARKER
from operator import mod
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.forms import CharField

CATEGORY_CHOICES = (
    ('M', 'Mobile'),
    ('T', 'Tablet'),
    ('L', 'Laptop'),
    ('F', 'Fashion'),
    ('G', 'Gadgets'),
    ('H', 'None'), 
)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    
    # def __str__(self):
    #     return self.name



class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    desc = models.TextField(null=True, blank=True)
    price = models.FloatField()
    image = models.ImageField(null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=100,default = 'N')
    color = models.CharField(max_length=100, null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=False)

    def __str__(self):
        return str(self.name)


class Order(models.Model):
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    @property
    def get_final_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_no_of_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item  in orderitems])
        return total

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product}--{self.quantity}"


class ShippingAddress(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.TextField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.address)
