from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # домашняя страница, на которой отображены все товары
    path('', views.Products.as_view(), name='home'),
    # поиск товара по слову в его названии
    path('search/', views.SearchView.as_view(), name="search"),
    # корзина
    path('cart/', views.Cart.as_view(), name='cart'),
    # сравнение
    path('comparison/', views.Comparison.as_view(), name='comparison'),
    # dashboard
    path('plot1/', views.plotly1, name='plot1'),
    # переход по категориям на navbar
    path('categories/<slug:slug>/', views.ProductsView.as_view(), name="products"),

    # урлы для нашего апи
    path('api/addToCart', views.add_to_cart, name='add_to_cart'),  # добавление товара в корзину
    path('api/deleteFromCart/<int:id>', views.delete_from_cart, name='delete_from_cart'),  # удаление товара с корзины
    path('api/addToComparison', views.add_to_comparison, name='add_to_comparison'),  # добавление товара в сравнения
    # удаление товара с сравнения
    path('api/deleteFromComparison/<int:id>', views.delete_from_comparison, name='delete_from_comparison'),
    # получение количества товаров в корзине и сравнение для уведомлений на navbar
    path('api/getCartItemsAmount', views.get_amount_of_items, name='itemsAmount'),
]

if settings.DEBUG:
    # если девелопмент, для дебага и просмотра даных на странице, которые отдают views
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
