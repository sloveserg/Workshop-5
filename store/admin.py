from django.contrib import admin

from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'slug']
    readonly_fields = ('slug',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount', 'discount_price', 'category', 'amount', 'date']
    list_select_related = ['category']
    list_filter = ['category']
    search_fields = ['name', 'description']
    fields = ['name', 'description', 'image', 'price', 'discount', 'discount_price', 'category', 'amount', 'date']
    autocomplete_fields = ['category']
    readonly_fields = ('date', 'slug', 'discount_price')


@admin.register(Order)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'name', 'surname', 'address', 'date', 'final_price']
    list_filter = ['date']
    search_fields = ['email', 'phone', 'name', 'surname']
    fields = ['email', 'phone', 'name', 'surname', 'address', 'date', 'title', 'final_price']
    readonly_fields = ('date', 'final_price')


@admin.register(OrderItem)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'amount', 'price', 'total_price']
    list_filter = ['order']
    search_fields = ['order', 'product']
    fields = ['product', 'order', 'amount', 'price', 'total_price']
    readonly_fields = ('price', 'total_price')
