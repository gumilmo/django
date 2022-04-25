from django.urls import path
from .views import test_vies, ProductDetailView

urlpatterns = [
    path('', test_vies, name='base'),
    path('products/<str:ct_model>/<str:slug>', ProductDetailView.as_view(), name='product_detail')
]

