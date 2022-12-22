
from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<str:string>', views.category, name='category'),
    path('product_detail/<int:pk>', views.ProductView, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path("after_payment/", views.after_payment, name="after_payment"),
    path('address/', views.shipaddress, name='address'),
    path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    path('quantity_increase/<int:id>', views.quantity_increase, name='quantity_increase'),
    path('quantity_decrease/<int:id>', views.quantity_decrease, name='quantity_decrease'),
    path('delete_item/<int:id>', views.delete_item, name='delete_item'),
    path('update_address/<int:id>', views.update_address, name='update_address'),
    
    # # Login / Register / Logout
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    
    
]
