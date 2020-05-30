# Generated by Django 3.0.6 on 2020-05-27 20:11

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import store.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, blank=True, editable=False, unique=True)),
                ('image', models.ImageField(default='default.jpg', upload_to='images/categories/')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(editable=False, max_length=254, validators=[django.core.validators.EmailValidator()])),
                ('phone', models.CharField(editable=False, max_length=13, validators=[store.validators.phone_number_validator])),
                ('name', models.CharField(editable=False, max_length=32)),
                ('surname', models.CharField(editable=False, max_length=32)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('title', models.CharField(blank=True, max_length=150)),
                ('final_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, blank=True, editable=False, unique=True)),
                ('price', models.DecimalField(decimal_places=0, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('discount', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('discount_price', models.DecimalField(decimal_places=0, default=Decimal('0'), editable=False, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('image', models.ImageField(default='default.jpg', upload_to='images/products/')),
                ('description', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('amount', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Category')),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Product')),
            ],
        ),
    ]
