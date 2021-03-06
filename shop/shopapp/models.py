import sys

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.utils import timezone
from galleryfield.fields import GalleryField

from PIL import Image
from io import BytesIO

User = get_user_model()

def get_model_for_count(*model_names):
    return (models.Count(model_name) for model_name in model_names)

def get_product_url(obj, viewname):

    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': 'store', 'slug': obj.slug})

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

class CategoryManager(models.Manager):


    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_filter(self):
        #qs = self.get_queryset().annotate(models.Count('anyshoes'))
        #print(AnyShoes.objects.all().filter(gender=0))
        # models = get_model_for_count('anyshoes')
        # queryset = self.get_queryset().annotate(*models).values()
        # #print([dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_COUNT_NAME[c['name']]]) for c in queryset][1:])
        # print(queryset.anyshoes__count)
        # return queryset
        #return qs
        pass
        #return [category_qs, gender_qs, season_qs]

class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()


    def __str__(self):
        return self.name

class Product(models.Model):

    VALID_RES = (400, 400)
    MAX_RES = (900,900)

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Название товара')
    slug = models.SlugField(unique=True)
    image = models.ImageField()
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image1 = self.image
        image2 = self.image2
        image3 = self.image3

        img1 = Image.open(image1)
        img2,img3 = 0,0
        if image2:
            img2 = Image.open(image2)
            new_img2 = img2.convert('RGB')
            filestream2 = BytesIO()
            new_img2.save(filestream2, 'JPEG', quality=90)
            filestream2.seek(0)
            name2 = '{}.{}'.format(*self.image2.name.split('.'))
            self.image2 = InMemoryUploadedFile(
                filestream2, 'ImageFiled', name2, 'jpeg/image', sys.getsizeof(filestream2), None
            )
        if image3:
            img3 = Image.open(image3)
            new_img3 = img3.convert('RGB')
            filestream3 = BytesIO()
            new_img3.save(filestream3, 'JPEG', quality=90)
            filestream3.seek(0)
            name3 = '{}.{}'.format(*self.image3.name.split('.'))
            self.image3 = InMemoryUploadedFile(
                filestream3, 'ImageFiled', name3, 'jpeg/image', sys.getsizeof(filestream3), None
            )

        new_img1 = img1.convert('RGB')

        min_height, min_width = self.VALID_RES

        #resized_img_max1 = new_img1.resize((800, 800), Image.ANTIALIAS)
        #resized_img_max2 = new_img2.resize((800, 800), Image.ANTIALIAS)
        #resized_img_max3 = new_img3.resize((800, 800), Image.ANTIALIAS)

        filestream1 = BytesIO()

        new_img1.save(filestream1, 'JPEG', quality=90)

        filestream1.seek(0)

        name1 = '{}.{}'.format(*self.image.name.split('.'))

        self.image = InMemoryUploadedFile(
            filestream1, 'ImageFiled', name1, 'jpeg/image', sys.getsizeof(filestream1) ,None
        )

        super().save(*args, *kwargs)

class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Пользователь', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_product')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Итого')

    def __str__(self):
        return "Продукты: {} для корзины".format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.total_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=7, default=0, decimal_places=2, verbose_name='Итого')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)



class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    adress = models.CharField(max_length=255, verbose_name='Адресс', null=True, blank=True)
    order = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


class Season(models.Model):

    name = models.CharField(max_length=255, verbose_name="Сезон года")

    def __str__(self):
        return self.name


class Size(models.Model):

    size = models.CharField(max_length=4, verbose_name="Размер")

    def __str__(self):
        return self.size

class Gender(models.Model):

    name = models.CharField(max_length=255, verbose_name="Пол")

    def __str__(self):
        return self.name

class Action(models.Model):

    name = models.CharField(max_length=255, verbose_name="Имя акции")
    discription = models.CharField(max_length=400, verbose_name="Описание акции")
    image = models.ImageField(verbose_name="Изображение", blank=True)

    def __str__(self):
        return self.name

class AnyShoes(Product):

    SIZE_CHOICES = [
        ('XS', '38'),
        ('S', '39'),
        ('M', '41'),
        ('M2', '42'),
        ('L', '44'),
        ('XL', '45'),
        ('XXL', 46)
    ]

    season = models.ForeignKey(Season, verbose_name="Сезон", on_delete=models.CASCADE)
    size = models.CharField(max_length=4, blank=True, verbose_name='Размер',choices=SIZE_CHOICES)
    gender = models.ForeignKey(Gender, verbose_name="Пол", on_delete=models.CASCADE)
    action = models.ForeignKey(Action, verbose_name="Акция товара", on_delete=models.CASCADE, null=True, blank=True)
    #size = models.ManyToManyField(Size, blank=True, related_name='related_size')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    def get_model_name(self):
        return self.__class__._meta.model_name


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOISES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ завершен')
    )

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    BUING_TYPE_CHOISES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name="Заказчик", related_name='related_orders', on_delete=models.CASCADE)
    fist_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    phone = models.CharField(max_length=10, verbose_name="Номер телефона")
    cart = models.ForeignKey(Cart, verbose_name='Корзина товаров', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name="Адресс", null=True, blank=True)
    email = models.EmailField(null=True,blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name="Статус заказа",
        choices=STATUS_CHOISES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name="Способ доставки",
        choices=BUING_TYPE_CHOISES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateTimeField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)






