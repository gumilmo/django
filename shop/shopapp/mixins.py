from django.shortcuts import render
from django.views.generic import View, FormView

from .models import Cart, Customer
from .froms import ProductForm

class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user = request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()

            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)

        self.cart = cart

        return super().dispatch(request, *args, **kwargs)

class FormSizeMixin(View):

    def get(self, request, *args, **kwargs):
        form = ProductForm(request.POST or None)
        context = {
            'form': form
        }
        self.form = form
        return render(request,context)

