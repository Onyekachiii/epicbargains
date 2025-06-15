from django.urls import path

from store import views 

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<slug>/", views.product_detail, name="product_detail"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("delete_cart_item/", views.delete_cart_item, name="delete_cart_item"),
    
    path('checkout/', views.create_order, name='checkout'),
    path("confirm-payment/<str:order_id>/", views.confirm_payment, name="confirm_payment"),
    path('checkout-success/', views.checkout_success, name='checkout_success')


]