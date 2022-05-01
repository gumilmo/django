from django.urls import path
from .views import (
    BaseView,
    ProductDetailView,
    filter_view,
    CartView,
    UserViewSet,
    AddToCartView,
    DeleteFromCartView,
    ChangeQTYView,
    ChekoutView,
    MakeOrderView,
    AboutView,
    ChangeSizeView,
)
from rest_framework import routers

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('products/<str:ct_model>/<str:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('api/filter', UserViewSet.as_view(), name='filter'),
    path('add-to-cart/<str:ct_model>/<str:slug>', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>', DeleteFromCartView.as_view(), name='remove-from-cart'),
    path('change-qty/<str:ct_model>/<str:slug>', ChangeQTYView.as_view(), name='change-qty'),
    path('change-size/<str:ct_model>/<str:slug>', ChangeSizeView.as_view(), name='change-size'),
    path('chekout/', ChekoutView.as_view(), name='chekout'),
    path('order/', MakeOrderView.as_view(), name='make_order'),
    path('about/',AboutView.as_view(), name='about'),
]

