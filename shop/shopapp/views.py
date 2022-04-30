from django.shortcuts import render
from django.views.generic import DetailView, View
from django.db.models import Avg, Max, Min
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from .models import AnyShoes, Category, Season, Gender, Customer, Cart, Size, CartProduct
from .mixins import CartMixin
from rest_framework.views import APIView
from .serializers import *
from rest_framework.generics import ListCreateAPIView
from django.contrib import messages

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

class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        #products = AnyShoes.objects.all()
        season = list(Season.objects.all())
        gender = list(Gender.objects.all())
        size = list(Size.objects.all())
        max_val = AnyShoes.objects.aggregate(Max('price'))

        #qs = filter(request)
        products = filter(request)

        context = {
            'products': products,
            'categories': categories,
            'season': season,
            'gender': gender,
            'size': size,
            'cart': self.cart,
        }

        return render(request, 'base.html', context)

def filter_view(request):
    return render(request, 'filter.html')

class ProductDetailView(CartMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'store': AnyShoes,
    }

    def dispatch(self, request,*args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        # self.context = {
        #     'size': list(Size.objects.all()),
        # }
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context

class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        context = {
            'cart': self.cart,
            'ct': categories,
        }

        return render(request, 'cart.html', context)

class UserViewSet(CartMixin, ListCreateAPIView):

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

class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'),kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user = self.cart.owner,
            cart=self.cart,
            content_type = content_type,
            object_id = product.id,
        )
        if created:
            self.cart.products.add(cart_product)
        self.cart.save()
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')

class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'),kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user = self.cart.owner,
            cart=self.cart,
            content_type = content_type,
            object_id = product.id,
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')

class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id,
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Колличество товара изменено ")
        print(request.POST)
        return HttpResponseRedirect('/cart/')






