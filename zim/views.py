from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Order, OrderItem, OrderItemAttribute, Product


def fetch_order(request):

    try:
        order_id = request.session['order']
        order = Order.objects.get(id=order_id)
    except:
        order = False

    return order


def home(request):

    products = Product.objects.all()
    return render(request, 'zim/home.html', {
        'products': products,
        'order': fetch_order(request)
    })


def products(request):
    products = Product.objects.all()[:120]

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 9)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'zim/products.html', {
        'products': products,
        'order': fetch_order(request)
    })


def product_detail(request, id):
    product = Product.objects.get(id=id)
    picked_products = Product.objects.all()[:4]
    return render(request, 'zim/product_detail.html', {
        'product': product,
        'picked_products': picked_products,
        'order': fetch_order(request)
    })


def add_to_cart(request):

    try:
        order_id = request.session['order']
        order = Order.objects.get(id=order_id)
    except:
        order = Order()
        order.save()

        request.session['order'] = order.id

    product = Product.objects.get(id=request.POST['product'])



    order_item = OrderItem(
        order=order,
        product=product,
        quantity=request.POST['quantity']
    )
    order_item.save()



    for attribute in product.productattribute_set.all():
        item_attribute = OrderItemAttribute(
            order_item=order_item,
            attribute=attribute.attribute,
            value=request.POST[attribute.attribute]

        )
        item_attribute.save()

    order_total = '{:0,.2f}'.format(order.order_total())

    return JsonResponse({
        'order_total': order_total,
        'order_count': order.orderitem_set.all().count()
    })


def checkout(request):
    return render(request, 'zim/checkout.html', {
        'order': fetch_order(request)

    })
