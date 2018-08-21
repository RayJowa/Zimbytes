from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^add_to_cart/$', views.add_to_cart, name='add_to_cart'),
    url(r'^affiliate_profile/$', views.affiliate_profile, name='affiliate_profile'),
    url(r'^change_affiliate/$', views.change_affiliate, name='change_affiliate'),
    url(r'^change_quantity/$', views.change_quantity, name='change_quantity'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^client_profile/$', views.client_profile, name='client_profile'),
    url(r'^delete_item/$', views.delete_item, name='delete'),
    url(r'^delete_order/$', views.detete_order, name='delete_order'),
    url(r'^new_profile/$', views.new_client_profile, name='new_profile'),
    url(r'^order/(?P<order>[0-9]+)/$', views.view_order, name='view_order'),
    url(r'^order_checkout/(?P<order>[0-9]+)/$', views.order_checkout, name='order_checkout'),
    url(r'^product_detail/(?P<id>[0-9]+)/$', views.product_detail, name='product_detail'),
    url(r'^products/$', views.products_page, name='products'),
    url(r'^products/(?P<category>[0-9]+)/$', views.products_cat, name='products_category'),
]