import sys

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse

from PIL import Image
from io import BytesIO

User = get_user_model()

def get_product_url(obj, viewname):

    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})

class MinResErrorExeption(Exception):
    pass

class LatestProductsManager():

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        products = []
        ct_models = ContentType.objects.filter(model__in=args)

        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)

        return products

class LatestProducts():

    objects = LatestProductsManager()

class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Category name')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):

    VALID_RES = (400, 400)
    MAX_RES = (900,900)

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Product name')
    slug = models.SlugField(unique=True)
    image = models.ImageField()
    description = models.TextField(verbose_name='Description', null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Price')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')

        min_height, min_width = self.VALID_RES


        resized_img_max = new_img.resize((800, 800), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_img_max.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        print(image.name, name, resized_img_max.width, resized_img_max.height)
        self.image = InMemoryUploadedFile(
            filestream, 'ImageFiled', name, 'jpeg/image', sys.getsizeof(filestream) ,None
        )

        super().save(*args, *kwargs)

class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='User', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Total Price')

    def __str__(self):
        return "Продукты: {} для корзины".format(self.product.title)

class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Total Price')

    def __str__(self):
        return str(self.id)

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Phone number')
    adress = models.CharField(max_length=255, verbose_name='Adress')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


class Season(models.Model):

    season_name = models.CharField(max_length=255, verbose_name="Сезон года")

    def __str__(self):
        return self.season_name


class Size(models.Model):

    size = models.CharField(max_length=4, verbose_name="Размер")

    def __str__(self):
        return self.size

class AnyShoes(Product):

    season = models.ForeignKey(Season, verbose_name="Сезон", on_delete=models.CASCADE)
    size = models.ForeignKey(Size, verbose_name="Размер", on_delete=models.CASCADE)

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')