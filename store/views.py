from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin

from store.models import Product, Category, OrderItem, Order
from .forms import OrderForm
import json


class Products(ListView):
    template_name = 'home.html'  # дефолтный темплейт для возвращения
    model = Product  # модель, с которой работает данная класса

    def get_queryset(self, *args, **kwargs):
        """
        переписываем функцию queryset
        Возвращаем список, в котором продукты поделены на подсписки по 3 штуки
        Так нужно для отображения на странице продуктов в блоке по 3 штуки
        :param args:
        :param kwargs:
        :return:
        """
        query = Product.objects.all().order_by('discount_price')
        products = []
        for i in range(query.count()):
            # [[1, 2, 3] [5, 6, 7] [7]] вместо чисел у нас в списках находятся обьекты продуктов
            products.append(query[i * 3: (i + 1) * 3])
        return products


class ProductsView(ListView, SingleObjectMixin):
    """
    Тоже самое, что и Products, только возвращает продукты, которые совпадает с категорией !
    Django сам проверяет поле slug модели Category
    slug категории передается в html странице как {% url 'products' category.slug %}
    """
    template_name = 'home.html'
    model = Product  # модель, с которой работает данная класса

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Category.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        переписываем функцию queryset
        Возвращаем список, в котором продукты поделены на подсписки по 3 штуки
        Так нужно для отображения на странице продуктов в блоке по 3 штуки
        :return:
        """
        query = Product.objects.filter(category=self.object)
        products = []
        for i in range(query.count()):
            products.append(query[i * 3: (i + 1) * 3])
        return products


class SearchView(ListView):
    template_name = "home.html"

    def get_queryset(self):
        """
        Функция - фильтр данных по поиску
        проверяет, есть ли ввхождение введенных данных в поле name Продукта
        Стандартный очень корявый поиск Django
        :return:
        """
        query = self.request.GET.get('q')
        if query:
            query = Product.objects.filter(name__contains=query)
            products = []
            for i in range(query.count()):
                products.append(query[i * 3: (i + 1) * 3])
            return products
        else:
            raise Http404


class Cart(TemplateView):
    """
    Корзина
    """
    template_name = 'cart.html'
    form_class = OrderForm  # форма для заказа товаров

    def get_context_data(self, *args, **kwargs):
        """
        В context кладем товары, которые были добавлены в корзину ( сессию )
        генерируем форму и добавляем ее тоже в context
        :param args:
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])
        query = []
        for product_id in cart:
            query.append(Product.objects.get(id=product_id))
        context['data'] = query
        context['form'] = OrderForm()
        return context

    def post(self, *args, **kwargs):
        form = OrderForm(self.request.POST)  # передаем данные с формы с пост запроса в нашу форму
        if form.is_valid():
            """
            Если данные валидные, создаем запись в таблице Order
            Потом берем ID этой записи и создаем в таблице OrderItem записи, где 
            product_id это будет айди товара с корзины
            order_id это будет айди заказа, который мы только что создали
            Используем django.messages для оповещения юзера о успешном заказе
            """
            email = form.data['email']
            phone = form.data['phone']
            name = form.data['name']
            surname = form.data['surname']
            address = form.data['address']

            # создаем запись в таблице Order
            new_order = Order.objects.create(email=email,
                                             phone=phone,
                                             name=name,
                                             surname=surname,
                                             address=address,
                                             )

            cart = self.request.session.get('cart')
            for product_id in cart:
                # создаем записи в таблице OrderItem
                OrderItem.objects.create(product_id=product_id, order_id=new_order.id)
            messages.add_message(self.request, messages.INFO, 'Ваш заказ успешно оформлен!')

        context = self.get_context_data(**kwargs)
        context['form'] = form  # возвращаем форму !
        return self.render_to_response(context)


def add_to_cart(request):
    id = request.GET.get('id')  # достаем айди продукта с реквеста
    cart = request.session.get('cart', [])
    product = Product.get_or_none(id)

    if product is None:
        # если записи нет в бд
        return HttpResponse(json.dumps({"error": f"Product with such id={id} doesn't exist"}),
                            content_type="application/json",
                            status=400)
    elif product.id in cart:
        # если продукт уже в корзине
        return HttpResponse(json.dumps({"added": 0}),
                            content_type="application/json",
                            status=400)
    else:
        # если продукта нет в корзине, то добавляем
        cart.append(product.id)

    request.session['cart'] = cart  # переписываем корзину
    # status 200, ajax - success
    return HttpResponse(json.dumps({"added": 1}), content_type="application/json")


def delete_from_cart(request, id):
    """
    Функция удаляет айди товара со списка ( корзины)
    :param request:
    :param id:
    :return:
    """
    cart = request.session.get('cart', [])
    product = Product.get_or_none(id)

    if product is None:
        # если такого продукта нет в БД, то возвращаем такой json
        return HttpResponse(json.dumps({"error": f"Product with such id={id} doesn't exist"}),
                            content_type="application/json")
    elif id in cart:
        # если айди в корзине
        cart.remove(id)  # удялем с корзины
        request.session['cart'] = cart  # присваиваем новое значение корзине
        return redirect('cart')  # редирект на страницу с корзиной
    else:
        # если такого айди нет в корзине, то возвращаем такой json
        # по сути, если продукта нет в корзине, то он не отображается на странице
        # то-есть его можно удалить только отправив get запрос на api
        # и только в этом случае сработает этот if
        return HttpResponse(json.dumps({"removed": 0}), content_type="application/json")


def get_amount_of_items(request):
    """
    Функция возвращает словарь с количеством товаров в корзине/сравнении
    :param request:
    :return:
    """
    counter = 0
    for key, values in request.session.get('comparison', {}).items():
        counter += len(values)
    return HttpResponse(json.dumps(
        {
            "cartAmount": len(request.session.get('cart', [])),
            "comparisonAmount": counter
        }),
        content_type="application/json")


class Comparison(ListView):
    template_name = 'comparison.html'
    model = Product

    def get_queryset(self, *args, **kwargs):
        """
        Функция, которая вместо индексов продуктов в списке сравнений, прописывает обьекты модели, соответствующие
        данным ключам, чтоб можно было выписать информацию о продуктах на странице списка сравнений, ибо изначально
         в корзине и списке сравнений хранятся только ID товаров
        :param args:
        :param kwargs:
        :return:
        """
        comparison = self.request.session.get('comparison', {})
        query = {}
        for category, products in comparison.items():
            query[category] = [Product.objects.get(id=product_id) for product_id in products]
        return query


def add_to_comparison(request):
    id = request.GET.get('id')  # достаем id с реквеста
    comparison = request.session.get('comparison', {})
    product = Product.get_or_none(id)

    if product is None:
        # если товара нет в бд, возвращаем такой json
        # статус 400, чтоб ajax использовал error
        return HttpResponse(json.dumps({"error": f"Product with such id={id} doesn't exist"}),
                            content_type="application/json",
                            status=400)
    else:
        if product.category.name not in comparison:
            # если категории товара нет в сравнении, то создаем список с ID
            comparison[product.category.name] = [product.id]
        else:
            # если есть категория
            if product.id in comparison[product.category.name]:
                # если айди продукта уже в списке, то возвращаем такой json
                # статус 400, чтоб ajax использовал error
                return HttpResponse(json.dumps({"added": 0}),
                                    content_type="application/json",
                                    status=400)
            else:
                # если его нет в списке, то добавляем к данной категории айди товара
                comparison[product.category.name].append(product.id)
        request.session['comparison'] = comparison  # переписываем в сессию список сравнения
        # дефолтный статус 200, ajax вызовет success
        return HttpResponse(json.dumps({"added": 1}), content_type="application/json")


def delete_from_comparison(request, id):
    """
    Функция удаляет товар с списка сравнений
    :param request:
    :param id:
    :return:
    """
    comparison = request.session.get('comparison', {})
    product = Product.get_or_none(id)

    if product is None:
        return HttpResponse(json.dumps({"error": f"Product with such id={id} doesn't exist"}),
                            content_type="application/json")
    else:
        if id in comparison[product.category.name]:
            comparison[product.category.name].remove(id)
            if not comparison[product.category.name]:
                #  если список (значение) в списке сравнений под ключем категории пустой, то мы его удаляем
                # чтоб категория не отображалась на странице списка сравнений
                del comparison[product.category.name]
            request.session['comparison'] = comparison  # присваиваем списку сравнений в сессии новый список сравнений
            return redirect('comparison')
        else:
            return HttpResponse(json.dumps({"removed": 0}), content_type="application/json")


def plotly1(request):
    import plotly
    import plotly.graph_objs as go
    from django.db.models.functions import TruncDay
    from django.db.models import Count

    # считаем количество заказов всех товаров
    # делаем group_by по product: annotate(acount=Count('product'))
    # values('product__name') возвращает нужные нам значения
    query = OrderItem.objects.values('product__name').annotate(acount=Count('product'))  # group by product

    bar = go.Bar(
        x=[item['product__name'] for item in query],  # название товара
        y=[item['acount'] for item in query]  # количество покупок
    )

    # считаем количество заказов товаров каждый день
    # select_related('order') -> inner join на таблицу Order
    # annotate(date=TruncDay('order__date')) group_by по дате, когда заказ был составлен
    # TruncDay('order__date') делает group by по дате, НО по ДНЮ
    # .annotate(acount=Count('product')) считаем количество товаров по дню ( как COUNT() в sql)
    query1 = OrderItem.objects.select_related('order').annotate(date=TruncDay('order__date')).values(
        'date').annotate(acount=Count('product')).order_by('date')

    bar1 = go.Bar(
        x=[item['date'].strftime("%d/%m/%Y") for item in query1],  # дата в таком-то формате
        y=[item['acount'] for item in query1]  # количество
    )

    graphJSON = json.dumps([bar, bar1], cls=plotly.utils.PlotlyJSONEncoder)
    return render(request, 'plot1.html', {'graphJSON': graphJSON, "ids": [0, 1]})
