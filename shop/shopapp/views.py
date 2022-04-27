from django.shortcuts import render
from django.views.generic import DetailView, View
from .models import AnyShoes, Category, LatestProducts, Season, Gender

class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = list(Category.objects.all())
        products = AnyShoes.objects.all()
        season = list(Season.objects.all())
        gender = list(Gender.objects.all())
        print(products[0])
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