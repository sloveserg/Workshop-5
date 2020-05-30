from django.db import models
from django.db.models import Sum
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator, validate_email
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from slugify import slugify
from PIL import Image
from .validators import phone_number_validator


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, editable=False)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, to_lower=True)

        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=128, unique=True)

    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, editable=False)

    price = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal(0),
                                validators=[MinValueValidator(Decimal(0))])

    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)],
                                           default=0)  # скидка

    discount_price = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal(0),
                                         validators=[MinValueValidator(Decimal(0))], editable=False)

    image = models.ImageField(upload_to='images/products/')

    description = models.TextField(editable=True)

    date = models.DateTimeField(default=now, editable=False)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # если удалить категорию, то удалятся все товары

    amount = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def get_description(self):
        """
        Возвращаем список характеристик
        Делаем сплит по знаку новой линии, чтоб получить список
        :return:
        """
        return self.description.split("\n")[:7]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, to_lower=True)  # чтоб убрать лишние символы с названия товара
        self.discount_price = self.price - self.price * Decimal(self.discount / 100)  # цена с учетом скидки

        super().save(*args, **kwargs)

        # запис картинки
        with Image.open(self.image.path) as img:
            img = img.resize((339, 347))
            img.save(self.image.path, "JPEG")

    @staticmethod
    def get_or_none(pk):
        """
        Метод для вытаскивания продукта по ключу
        Нужен для того, чтоб не писать каждый раз try except
        :param pk:
        :return:
        """
        try:
            product = Product.objects.get(id=pk)
        except ObjectDoesNotExist as e:
            product = None
        return product


class Order(models.Model):
    email = models.EmailField(validators=[validate_email])
    phone = models.CharField(max_length=13, validators=[phone_number_validator])
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    address = models.CharField(max_length=64)
    date = models.DateField(default=now)
    title = models.CharField(blank=True, max_length=150)
    final_price = models.DecimalField(default=0.00, decimal_places=0, max_digits=20)

    objects = models.Manager()

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        order_items = self.order_items.all()
        self.final_price = order_items.aggregate(Sum('total_price'))[
            'total_price__sum'] if order_items.exists() else 0.00  # суммирует стоимость всех продуктов в заказе
        self.title = f"Order {self.id}"  # пишет Order + его айди
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # если удалить продукт, удалится OrderItem
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='order_items')  # тоже самое, только с заказом
    amount = models.PositiveIntegerField(default=1)
    price = models.DecimalField(default=0.00, decimal_places=0, max_digits=20)
    total_price = models.DecimalField(default=0.00, decimal_places=0, max_digits=20)

    def __str__(self):
        return f'{self.product.name}'

    def save(self, *args, **kwargs):
        self.price = self.product.discount_price
        self.total_price = Decimal(self.amount) * Decimal(self.price)
        super().save(*args, **kwargs)
        self.order.save()
        # Используем order.save(), чтоб при добавлении новых продуктов к заказу, в
        # записи в таблице Order происходило обновление конечной стоимости всех товаров
