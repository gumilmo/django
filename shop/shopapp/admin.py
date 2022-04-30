from django.forms import ModelChoiceField, ModelForm, ValidationError
from django.contrib import admin
from .models import *

from PIL import Image

class ShoesAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Загружайте изображения с миниальным разрешение {}x{}'.format(
            *Product.VALID_RES
        )


class ShoesAdmin(admin.ModelAdmin):

    form = ShoesAdminForm


admin.site.register(AnyShoes, ShoesAdmin)
admin.site.register(Season)
admin.site.register(Size)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Category)
admin.site.register(Gender)
admin.site.register(Order)
