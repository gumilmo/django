from django.shortcuts import render
from django.views.generic import DetailView, View
from django.db.models import Avg, Max, Min
from .models import AnyShoes, Category, Season, Gender, Customer, Cart

from rest_framework.views import APIView
from .serializers import *
from rest_framework.generics import ListCreateAPIView

# from django_filters.rest_framework import DjangoFilterBackend
# from django_filters import rest_framework as filters

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

def is_valid_queryparam(param):
    return param != '' and param is not None

def filter(request):
    products = AnyShoes.objects.all()

    category_chk_query = request.GET.get('category_chk')
    gender_chk_query = request.GET.get('gender_chk')
    season_chk_query = request.GET.get('season_chk')
    min_price_query = request.GET.get('min_price')
    max_price_query = request.GET.get('max_price')

    if is_valid_queryparam(category_chk_query):
        products = products.filter(category__name__icontains=category_chk_query)
    elif is_valid_queryparam(gender_chk_query):
        products = products.filter(gender__name__icontains=gender_chk_query)
    elif is_valid_queryparam(season_chk_query):
        products = products.filter(season__name__icontains=season_chk_query)

    if is_valid_queryparam(min_price_query):
        products = products.filter(price__gte=min_price_query)
    if is_valid_queryparam(max_price_query):
        products = products.filter(price__lte=max_price_query)

    return products

class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        #products = AnyShoes.objects.all()
        season = list(Season.objects.all())
        gender = list(Gender.objects.all())
        max_val = AnyShoes.objects.aggregate(Max('price'))

        #qs = filter(request)
        products = filter(request)

        context = {
            'products': products,
            'categories': categories,
            'season': season,
            'gender': gender,
        }

        return render(request, 'base.html', context)

def filter_view(request):
    return render(request, 'filter.html')

class ProductDetailView(DetailView):

    CT_MODEL_MODEL_CLASS = {
        'store': AnyShoes
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

class CartView(View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(owner=customer)
        categories = list(Category.objects.all())
        context = {
            'cart': cart,
            'ct': categories,
        }

        return render(request, 'cart.html', context)

class UserViewSet(ListCreateAPIView):

    serializer_class = AnyShoesSerializer
    #filter_backends = (DjangoFilterBackend)

    def get_queryset(self):
        qs = AnyShoes.objects.all()
        title = self.request.query_params.get('title')
        if title is not None:
            qs = qs.filter(title__icontains=title)
        return qs
    # renderer_classes = [ListCreateAPIView]
    # template_name = 'base.html'
    #
    # def get(self, request):
    #     # Получаем набор всех записей из таблицы Capital
    #     queryset = AnyShoes.objects.all()
    #     # Сериализуем извлечённый набор записей
    #     serializer_for_queryset = AnyShoesSerializer(
    #         instance=queryset,  # Передаём набор записей
    #         many=True  # Указываем, что на вход подаётся именно набор записей
    #     )
    #     return Response(serializer_for_queryset.data)


# class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
#     pass
#
# class ProductFilter(filters.CharFilter):
#
#     class Meta:
#         model = AnyShoes
#         fields = ['title']








