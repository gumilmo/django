from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'


    order_date = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Order
        fields = (
            'fist_name',
            'last_name',
            'email',
            'phone',
            'address',
            'buying_type',
            'order_date',
            'comment'
        )