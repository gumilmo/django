from django.shortcuts import render
from django.views.generic import DetailView, View
from django.db.models import Avg, Max, Min
from .models import AnyShoes, Category, LatestProducts, Season, Gender

def is_valid_queryparam(param):
    return param != '' and param is not None

class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        products = AnyShoes.objects.all()
        season = list(Season.objects.all())
        gender = list(Gender.objects.all())
        max_val = AnyShoes.objects.aggregate(Max('price'))
        print(products[0])

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


        context = {
            'products': products,
            'categories': categories,
            'season': season,
            'gender': gender,
        }

        print(category_chk_query)
        #get_by_category = products.

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