from django.shortcuts import render
from django.views.generic import DetailView, View
from django.db.models import Avg, Max, Min
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from .models import AnyShoes, Category, Season, Gender, Customer, Cart, Size, CartProduct, Action
from .mixins import *
from rest_framework.views import APIView
from django.db import transaction
from .serializers import *
from rest_framework.generics import ListCreateAPIView
from django.contrib import messages
from .froms import OrderForm, ProductForm
from .utils import *
from django.views.generic.edit import FormMixin
# from django_filters.rest_framework import DjangoFilterBackend
# from django_filters import rest_framework as filters
from django.core.paginator import Paginator
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
    action_query = request.GET.get('action')

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

    if is_valid_queryparam(action_query):
        products = products.filter(action__name__icontains=action_query)

    return products

class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        #products = AnyShoes.objects.all()
        season = list(Season.objects.all())
        gender = list(Gender.objects.all())
        size = list(Size.objects.all())
        actions = list(Action.objects.all())
        max_val = AnyShoes.objects.aggregate(Max('price'))

        #qs = filter(request)
        products = filter(request)

        prodcuts_paginator = Paginator(products,6)
        page_num = request.GET.get('page')
        page = prodcuts_paginator.get_page(page_num)
        #page = prodcuts_paginator.get_elided_page_range(page)
        num_pages = "a"*page.paginator.num_pages

        context = {
            'products': page,
            'categories': categories,
            'season': season,
            'gender': gender,
            'size': size,
            'cart': self.cart,
            'actions': actions,
            'page': page,
            'num_pages': num_pages,
        }

        return render(request, 'base.html', context)

def filter_view(request):
    return render(request, 'filter.html')

class AboutView(View):

    def get(self, request):
        return render(request, 'about.html')

class ProductDetailView(CartMixin, FormMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'store': AnyShoes,
    }
    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'
    form_class = ProductForm

    def dispatch(self, request,*args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        context['form'] = ProductForm(initial={'post': self.object})
        print(self.get_form(),'+++')
        return context

    def form_valid(self, form):
        form.save()
        return super(AnyShoes, self).form_valid(form)

class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        form = ProductForm(request.POST or None)
        context = {
            'cart': self.cart,
            'ct': categories,
            'form': form,
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
        recalc_cart(self.cart)
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
        recalc_cart(self.cart)
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
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Колличество товара изменено ")
        return HttpResponseRedirect('/cart/')

class ChangeSizeView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        product = AnyShoes.objects.get(slug=product_slug)
        form = ProductForm(request.POST or None)
        if form.is_valid():
            product.size = form.cleaned_data['size']
        print(product.size, product.title)
        messages.add_message(request, messages.INFO, "Размер выбран")
        return HttpResponseRedirect('/cart/')


class ChekoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())

        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'ct': categories,
            'form': form,
        }

        return render(request, 'chekout.html', context)

class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        form = OrderForm(request.POST or None)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.fist_name = form.cleaned_data['fist_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.email = form.cleaned_data['email']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.order.add(new_order)
            messages.add_message(request, messages.INFO, "Спасибо за заказ! На вашу почту будет отправлено письмо с переходом на форму оплаты.")
            return HttpResponseRedirect('/chekout')
        messages.add_message(request, messages.INFO, "К сожаления произошла ошибка, повторите заказ снова")
        return HttpResponseRedirect('chekout/')

