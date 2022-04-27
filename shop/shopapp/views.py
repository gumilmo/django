from django.shortcuts import render
from django.views.generic import DetailView, View
from .models import AnyShoes, Category, LatestProducts

class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products = AnyShoes.objects.all()
        print(products)
        context = {
            'ct': categories,
            'products': products
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