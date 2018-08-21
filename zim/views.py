import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from .forms import ProfileForm, SaleForm
from .models import (Banner, Click, Delivery, Due, Order, OrderItem, OrderItemAttribute, Payment, Product, Profile,
                     Receipt, ReceiptDetail, Sale, ShippingDetails, SubCategory)


@login_required
def affiliate_profile(request):
    product = Product.objects.all()[1]
    user = request.user
    sales = user.affliliate_sale.all().order_by('-date')[:10]
    month_sales = user.affliliate_sale.all().filter(date__month=datetime.date.today().month).count()
    account_balance = user.profile.due_set.filter(paid=False, approved=True)

    level_0_comm = user.profile.due_set.filter(sale__date__month=datetime.date.today().month).filter(type='lvl_0_comm').aggregate(Sum('amount'))['amount__sum']

    if level_0_comm is None:
        level_0_comm = 0

    level_1_comm = 0
    level_2_comm = 0
    level_3_comm = 0
    for affiliate_1 in user.up_ref.all():
        for sale in affiliate_1.user.affliliate_sale.all():
            level_1_comm += sale.affiliate_commission_1()

        for affiliate_2 in affiliate_1.user.up_ref.all():
            for sale in affiliate_2.user.affliliate_sale.all():
                level_2_comm += sale.affiliate_commission_2()

            for affiliate_3 in affiliate_2.user.up_ref.all():
                for sale in affiliate_3.user.affliliate_sale.all():
                    level_3_comm += sale.affiliate_commission_3()

    # Total monthly commission
    month_comm = user.profile.due_set.filter(sale__date__month=datetime.date.today().month).filter(type='lvl_0_comm').aggregate(Sum('amount'))['amount__sum']

    payments = user.payment_set.all().order_by('-date')[:5]

    # Account balance
    dues = user.profile.due_set.exclude(type='cost_of_sales').aggregate(Sum('amount'))['amount__sum']
    if dues is None:
        dues = 0

    payments = user.payment_set.all().aggregate(Sum('amount'))['amount__sum']
    if payments is None:
        payments = 0

    account_balance = dues - payments

    return render(request, 'zim/affiliate_profile.html',
                  {
                      'account_balance': account_balance,
                      'product': product,
                      'sales': sales,
                      'month_sales': month_sales,
                      'month_comm': month_comm,
                      'level_0_comm': level_0_comm,
                      'level_1_comm': level_1_comm,
                      'level_2_comm': level_2_comm,
                      'level_3_comm': level_3_comm,
                      'total_comm': level_0_comm + level_1_comm + level_2_comm + level_3_comm,
                      'payments': payments,
                      'account_balance': account_balance
                   }
                  )


def new_client_profile(request):
    user = User.objects.get(username=request.user.username)

    if user.profile.completed:
        return HttpResponseRedirect(reverse('zim:home', kwargs={}))
    else:
        if request.method == 'POST':
            form = ProfileForm(request.POST)
            if form.is_valid():
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.profile.mobile_number = form.cleaned_data['mobile_number']
                user.profile.completed = True
                user.save()

                return HttpResponseRedirect(reverse('zim:home', kwargs={})) #TODO change this to view profile page
        else:
            form = ProfileForm(initial={
                'date_of_birth': datetime.date(1992, 6, 1),
                'first_name': request.user.first_name,
                'last_name': request.user.last_name
            })

        return render(request, 'zim/new_profile.html', {'form': form, 'ray': 'ray'})


@login_required
def client_profile(request):
    user = request.user
    product = Product.objects.get(id=9)
    all_products = Product.objects.all()
    orders = user.order_set.all()
    return render(request, 'zim/order_list.html',
                  {'product': product,
                   'products': all_products,
                   'orders': orders
                   }
                  )


def fetch_order(request):

    try:
        order_id = request.session['order']
        order = Order.objects.get(id=order_id)
    except:
        order = False

    return order


def home(request):
    banners = Banner.objects.filter(active=True)

    products = Product.objects.all()
    return render(request, 'zim/home.html', {
        'products': products,
        'order': fetch_order(request),
        'banners':banners
    })


def products_page(request):
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


def products_cat(request, category):

    products = Product.objects.filter(category__id=category)[:120]

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

    try:
        user = User.objects.get(username=request.user.username)
    except:
        user = None

    Click(user=user, product=product).save()

    picked_products = Product.objects.all().annotate(clicks=Count('click')).order_by('-clicks')[:4]
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
        order.order_number = '0'*(6-len(str(order.id)))+str(order.id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user.username)
            order.user = user

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


def change_affiliate(request):
    # TODO handle where affiliate is not found
        profile = Profile.objects.get(affiliate_code=request.POST['affiliate'])

        return JsonResponse({
            'profile': profile.user.username
        })


def change_quantity(request):
    item = OrderItem.objects.get(id=request.POST['item_id'])
    item.quantity = int(request.POST['quantity'])
    item.save()

    return JsonResponse({
        'new_price': item.item_total(),
        'new_order_total': item.order.order_total()
    })


def delete_item(request):
    item = OrderItem.objects.get(id=request.POST['item_id'])
    order = item.order
    item.delete()

    order_total = '{:0,.2f}'.format(order.order_total())
    return JsonResponse({
        'order_total': order_total,
        'order_count': order.orderitem_set.all().count()
    })


def detete_order(request):
    order_id = request.POST['order_id']
    order = Order.objects.get(id=order_id)

    order.delete()

    return JsonResponse({
        'order_id': order_id
    })


def checkout(request):

    order = fetch_order(request)
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        order.user = user
        order.save()
    else:
        user = False

    if request.method == 'POST':

        form = SaleForm(request.POST)
        if form.is_valid():
            # Save shipping details
            shipping_details = form.save(commit=True)
            sale = Sale()
            sale.amount = order.order_total()
            sale.order = order

            # Get current user(buyer)
            if request.user.is_authenticated:
                buyer = User.objects.get(username=request.user.username)
                sale.buyer = buyer

            # Get affiliate (who refered the sale and earns commission
            profile = Profile.objects.get(affiliate_code=request.POST['affiliate'])
            affiliate = profile.user
            sale.affiliate = affiliate

            # Link sale to shipping details
            sale.shipping_details = shipping_details
            sale.save()

            # Collect money
            collect_m = collect_money(
                request.POST['ecocash_phone'],
                order.order_total()
            )

            if collect_m['status'] == 'Success':

                # Record receipt after collecting money
                receipt = Receipt(
                    receipt_detail=collect_m['receipt_detail'],
                    amount=order.order_total(),  # passed to, and returned from collect money
                    payer=shipping_details,
                )
                receipt.save()
                sale.receipt = receipt
                sale.save()

                # Record what's due to supplier
                for item in order.orderitem_set.all():

                    supplier_due = Due(
                        recipient=item.product.supplier.profile,
                        amount=item.product.commission_category.supplier * item.item_total(),
                        narration='{} x {} to {} {}'.format(item.quantity,
                                                            item.product.name,
                                                            sale.shipping_details.first_name,
                                                            sale.shipping_details.last_name
                                                            ),
                        type='cost_of_sales',
                        sale=sale
                    )
                    supplier_due.save()
                    if sale.affiliate:
                        commission_0 = Due(
                            recipient=sale.affiliate.profile,
                            amount=item.product.commission_category.affiliate_level_0 * item.item_total(),
                            narration='First level commission',
                            type='lvl_0_comm',
                            sale=sale
                        )
                        commission_0.save()

                    if affiliate.profile.affiliate_ref:
                        commission_1 = Due(
                            recipient=affiliate.profile.affiliate_ref.profile,
                            amount=item.product.commission_category.affiliate_level_1 * item.item_total(),
                            narration='Second level commission',
                            type='lvl_1_comm',
                            sale=sale

                        )
                        commission_1.save()

                    if affiliate.profile.affiliate_ref.profile.affiliate_ref:
                        commission_1 = Due(
                            recipient=affiliate.profile.affiliate_ref.profile.affiliate_ref.profile,
                            amount=item.product.commission_category.affiliate_level_2 * item.item_total(),
                            narration='Third level commission',
                            type='lvl_2_comm',
                            sale=sale

                        )
                        commission_1.save()



                delivery = Delivery(
                    sale=sale,
                    status='Awaiting pickup'
                )
                delivery.save()

                order.status = 'awaiting_shipment'
                order.save()

                messages.success(request, 'Successful! You will be notified of delivery shortly')
                request.session['order'] = ''
                
            else:
                pass
                messages.error(request, 'Failed to collect money. Reason:___')

            return render(request, 'zim/checkout.html', {})

    else:
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user.username)

            data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.profile.mobile_number,
                'email': user.email,
            }
            form = SaleForm(initial=data)
        else:
            form = SaleForm()

    return render(request, 'zim/checkout.html', {
        'order': order,
        'form': form,
        'user': user
    })


def order_checkout(request, order):
    order = Order.objects.get(id=order)
    return render(request, 'zim/checkout.html', {
        'order': order
    })


def collect_money(ecocash_number, amount):
    # Put link to collection API here

    # if success
    status = 'Success'

    # save transaction
    receipt_detail = ReceiptDetail(
        phone_number=ecocash_number,
        amount=amount,
        payment_method= 'Ecocash',
        ref='receipt_ref',  # This should be returned by the API
        identifier='second ID',  # in case there's more from API
         )
    receipt_detail.save()

    return {
        'status': status,
        'receipt_detail': receipt_detail
    }


def view_order(request, order):
    order = Order.objects.get(id=order)
    product = Product.objects.get(id=9)

    status_assign = {
        'awaiting_payment': 1,
        'awaiting_shipment': 2,
        'shipped': 3,
        'confirmed': 4
    }

    return render(request, 'zim/single_order.html', {
        'order': order,
        'order_status_count': status_assign[order.status],
        'product': product,
    })
