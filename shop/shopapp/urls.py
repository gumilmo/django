from django.urls import path
from .views import BaseView, ProductDetailView, filter_view, CartView, UserViewSet,AddToCartView
from rest_framework import routers

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('products/<str:ct_model>/<str:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('api/filter', UserViewSet.as_view(), name='filter'),
    path('add-to-cart/<str:ct_model>/<str:slug>', AddToCartView.as_view(), name='add_to_cart'),
]

