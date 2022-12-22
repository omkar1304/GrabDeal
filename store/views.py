
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from .models import *
from django.contrib.auth.models import User, auth
from .models import Customer, ShippingAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from ecommerce.settings import LOGIN_REDIRECT_URL
from django.core.paginator import Paginator
from . forms import UpdateForm
from django.views.decorators.csrf import csrf_exempt
import random

@csrf_exempt
class ProductView(LoginRequiredMixin,DetailView):
    model = Product
    template_name = 'store/product.html'
    context_object_name = 'product'
    
@csrf_exempt     
def store(request):
    # search idea ->
    
    search_input = request.GET.get('search_input') or ''
    # if user enters something then show related items only
    if search_input:
        products = Product.objects.filter(name__contains=search_input)
    # else show all items
    else:
        products = Product.objects.all().order_by('?')
        
    # paginating ->
    
    paginator = Paginator(products, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        order = {'get_no_of_items': 0, 'get_final_total': 0}
        items = []

    context = {'page_obj': page_obj, 'items': items, 'order': order}
    return render(request, 'store/index.html', context)

@csrf_exempt
def category(request, string):
    products = Product.objects.filter(category=string).order_by('?')
    print(products)
    #paginating ->
    
    paginator = Paginator(products, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        order = {'get_no_of_items': 0, 'get_final_total': 0}
        items = []

    context = {'page_obj': page_obj, 'items': items, 'order': order}
    return render(request, 'store/index.html', context)
    


@login_required(login_url=LOGIN_REDIRECT_URL)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        order = {'get_no_of_items': 0, 'get_final_total': 0}
        items = []

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)

@csrf_exempt
@login_required(login_url=LOGIN_REDIRECT_URL)
def add_to_cart(request, id):
    customer = request.user.customer
    product = Product.objects.get(id=id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    if not OrderItem.objects.filter(product=product, order=order).exists():
        OrderItem.objects.create(product=product, order=order)
    else:
        orderitem = OrderItem.objects.filter(product=product).all().values()
        for i in orderitem:
            count = i['quantity']

        orderitem.update(quantity=count + 1)

    return redirect('store')

@csrf_exempt
def quantity_increase(request, id):
    customer = request.user.customer
    product = Product.objects.get(id=id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem = OrderItem.objects.filter(product=product, order=order).all().values()
    for i in orderitem:
        count = i['quantity']

    orderitem.update(quantity=count + 1)

    return redirect('cart')

@csrf_exempt
def quantity_decrease(request, id):
    customer = request.user.customer
    product = Product.objects.get(id=id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem = OrderItem.objects.filter(product=product, order=order).all().values()
    for i in orderitem:
        count = i['quantity']

    if count - 1 <= 0:
        orderitem = OrderItem.objects.get(product=product, order=order)
        orderitem.delete()
    else:
        orderitem.update(quantity=count - 1)

    return redirect('cart')

@csrf_exempt
def delete_item(request, id):
    customer = request.user.customer
    product = Product.objects.get(id=id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem = OrderItem.objects.get(product=product, order=order)
    orderitem.delete()
    return redirect('cart')

@csrf_exempt
@login_required(login_url=LOGIN_REDIRECT_URL)
def checkout(request):
    if request.method == "POST":
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zipcode = request.POST['zipcode']
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
        shippingaddress, created = ShippingAddress.objects.update_or_create(customer=customer, order=order, address=address, city=city, state=state, country=country, zipcode=zipcode)
        shippingaddress.save()
            
        return redirect('checkout')    
            
    else:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        shippingaddress = ShippingAddress.objects.get_or_create(customer=customer, order=order)
        items = order.orderitem_set.all()
        
        context = {'items': items, 'order': order,'shippingaddress': shippingaddress}
        
        return render(request, 'store/checkout.html', context)


@csrf_exempt
def shipaddress(request):
    
    try:
        if request.method == "POST":
            
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            country = request.POST['country']
            zipcode = request.POST['zipcode']
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            
            shippingaddress = ShippingAddress(customer=customer, order=order, address=address, city=city, state=state, country=country, zipcode=zipcode)
            shippingaddress.save()
            
            return redirect('store')
    except Exception as e:
        messages.info(request, "Address already added!")
        return redirect('store')
    else:
        return render(request, 'store/address.html')

@csrf_exempt
@login_required(login_url=LOGIN_REDIRECT_URL)
def update_address(request, id):
    if request.method == 'POST':
        ud = ShippingAddress.objects.get(pk=id)
        form = UpdateForm(request.POST, instance=ud)
        if form.is_valid():
            form.save()
        messages.info(request, "Address updated successfully!")
        return redirect('checkout')
    else:
        ud = ShippingAddress.objects.get(pk=id)
        form = UpdateForm(instance=ud)
        return render(request, 'store/update_address.html', {'form': form})
    
@csrf_exempt
def after_payment(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem = OrderItem.objects.filter(order=order)
    orderitem.delete()
    messages.info(request, "Thank you for shopping! Your transaction has been completed.")
    return redirect('store')
 

       
# Login / Register / Logout


@csrf_exempt
def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "User Name Taken")
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect('register')

            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                password=password1, email=email)
                user.save()
                # as soon as if user create account then we also have to create customer account
                customer, created = Customer.objects.get_or_create(user=user,name=user.username, email=user.email)
                customer.save()
                if user is not None:
                    auth.login(request, user)
               
                
                return redirect('address')
        else:
            messages.info(request, "Password Not Matching")
            return redirect('register')


    else:
        return render(request, 'store/register.html')
    return redirect('store')

@csrf_exempt
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            # print(user)
            # customer, created = Customer.objects.get_or_create(user=user, name=request.user.username, email=request.user.email)
            # customer.save()
            return redirect('store')
        else:
            messages.info(request, "Invalid Info")
            return redirect('login')

    else:
        return render(request, "store/login.html")
        
@csrf_exempt
def logout(request):
    auth.logout(request)
    return redirect('store')