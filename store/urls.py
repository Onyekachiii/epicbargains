from django.urls import path

from store import views 

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<slug>/", views.product_detail, name="product_detail"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart")
]