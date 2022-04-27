from django.shortcuts import render
from django.views.generic import DetailView, View
from django.db.models import Avg, Max, Min
from .models import AnyShoes, Category, LatestProducts, Season, Gender

class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        products = AnyShoes.objects.all()
        season = list(Season.objects.all())
        gender = list(Gender.objects.all())
        max_val = AnyShoes.objects.aggregate(Max('price'))
        print(products[0])

        category_chk_query = request.GET.get('category_chk')
        min_price_query = request.GET.get('min_price')

        if category_chk_query != '' and category_chk_query is not None:
            products = products.filter(category__name__icontains=category_chk_query)
        if min_price_query != '' and min_price_query is not None:
            products = products.filter(price__gte=min_price_query)


        context = {
            'products': products,
            'categories': categories,
            'season': season,
            'gender': gender,
            'max_val': max_val.values,
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