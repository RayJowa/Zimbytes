from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^add_to_cart/$', views.add_to_cart, name='add_to_cart'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^delete_item/$', views.detete_item, name='delete'),
    url(r'^product_detail/(?P<id>[0-9]+)/$', views.product_detail, name='product_detail'),
    url(r'^products/$', views.products, name='products'),
]