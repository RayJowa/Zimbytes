import pytz

from allauth.socialaccount.models import SocialAccount
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Count, Max, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


from Zimbytes.settings import ALLOWED_HOSTS
DEFAULT_COMMISSION_CATEGORY = 1


def upload_location(instance, filename):
    return 'images/products/%s/%s' % (instance.product.id, filename)


def upload_banners(instance, filename):
    return 'images/banners/' + filename


def upload_propic(instance, filename):
    return 'images/propics/' + instance.user.username


def upload_shopics(instance, filename):
    return 'images/shops/%s/%s' % (instance.id, filename)


class CommissionCategory(models.Model):
    name = models.CharField(max_length=20)
    supplier = models.DecimalField(max_digits=3, decimal_places=2)
    affiliate_level_0 = models.DecimalField(max_digits=3, decimal_places=2)
    affiliate_level_1 = models.DecimalField(max_digits=3, decimal_places=2)
    affiliate_level_2 = models.DecimalField(max_digits=3, decimal_places=2)
    affiliate_level_3 = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    deactivate = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def most_selling(self):
        most_sub = self.subcategory_set.all().annotate(sold=Count('product__orderitem')).order_by('sold')[0]
        most_sold = most_sub.product_set.all().annotate(sold=Count('orderitem')).order_by('sold')

        if len(most_sold) > 0:
            return most_sold[0]
        else:
            return most_sub.product_set.first()


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return '{} > {}'.format(self.category.name, self.name)


# TODO enable second level sub category
class SubCategory2(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return '{} > {}'.format(self.category.name, self.name)


class Collection(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    date_updated = models.DateTimeField(auto_now_add=True)  # TODO update this to when last 'updated'
    home_photo = models.ImageField(upload_to=upload_shopics,
                                   null=True,
                                   blank=True,
                                   width_field='width_field',
                                   height_field='height_field'
                                   )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    ''''
    def save(self, *args, **kwargs):
        try:
            image = Image.open(self.home_photo)
            current_aspect = self.width_field / self.height_field
            new_aspect = 4 / 3

            output = BytesIO()

            if current_aspect == new_aspect:
                pass
            elif current_aspect > new_aspect:
                rqw = new_aspect * self.height_field
                left = (self.width_field - rqw) / 2
                upper = 0
                right = left + rqw
                lower = self.height_field

                box = (left, upper, right, lower)
                new_image = image.crop(box)
                new_image.save(output, format='PNG', quality=100)
                output.seek(0)

                self.home_photo = InMemoryUploadedFile(output, 'ImageField',
                                                       "%s.jpg" % self.home_photo.name.split('.')[0],
                                                       'image/jpeg', sys.getsizeof(output), None)

                super(Collection, self).save()
            else:
                rqh = (3 / 4) * self.width_field
                left = 0
                upper = (self.height_field - rqh) / 2
                right = self.width_field
                lower = left + rqh
                box = (left, upper, right, lower)
                new_image = image.crop(box)
                new_image.save(output, format='PNG', quality=100)
                output.seek(0)

                self.home_photo = InMemoryUploadedFile(output, 'ImageField',
                                                       "%s.png" % self.home_photo.name.split('.')[0],
                                                       'image/jpeg', sys.getsizeof(output), None)

            super(Collection, self).save()
        except ValueError:
            super(Collection, self).save()
'''


class Product(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    commission_category = models.ForeignKey(CommissionCategory,
                                            on_delete=models.SET_NULL, null=True, default=DEFAULT_COMMISSION_CATEGORY)
    sale = models.BooleanField(default=False)
    category = models.ManyToManyField(SubCategory)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    def new(self):
        age = datetime.now(pytz.utc) - self.added
        if age.days < 30:
            return True
        else:
            return False

    def get_url(self):
        domain = ALLOWED_HOSTS[0]

        return 'http://%s:8000/product_detail/%s' % (domain, self.id)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field'
                              )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=20)

    def __str__(self):
        return self.product.name + ' ' + self.attribute


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.product.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=20)


class Order(models.Model):
    order_number = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(Session, blank=True, null=True, on_delete=models.SET_NULL)
    last_modified = models.DateTimeField(auto_now=True)
    status = models.CharField(default='awaiting_payment',
                              max_length=20,
                              blank=True,
                              choices=(
                                     ('confirmed', 'Confirmed'),
                                     ('shipped', 'Shipped'),
                                     ('awaiting_shipment', 'Awaiting shipment'),
                                     ('awaiting_payment', 'Awaiting payment')
                                 )
                              )
    paid_date = models.DateTimeField(null=True, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    confirmed_date = models.DateTimeField(null=True, blank=True)

    def order_total(self):
        total = 0

        for item in self.orderitem_set.all():
            total += item.quantity * item.product.price

        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def item_total(self):
        return self.product.price * self.quantity


class OrderItemAttribute(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=20)
    value = models.CharField(max_length=20)


class BankingDetails(models.Model):
    bank = models.CharField(max_length=20)
    branch = models.CharField(max_length=20)
    branch_code = models.CharField(max_length=20)
    account_number = models.CharField(max_length=30)

    def __str__(self):
        return self.bank


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=25, blank=True)
    phone_verified = models.BooleanField(default=False)
    user_type = models.CharField(default='client',
                                 max_length=20,
                                 blank=True,
                                 choices=(
                                     ('client', 'client'),
                                     ('supplier', 'supplier'),
                                     ('affiliate', 'affiliate')
                                 )
                                 )
    banking_details = models.ForeignKey(BankingDetails, blank=True, null=True, on_delete=models.CASCADE)
    birth_date = models.DateField(blank=True, null=True)
    town = models.CharField(max_length=30, blank=True)
    completed = models.BooleanField(default=False)
    client_ref = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='affiliate')
    affiliate_ref = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='up_ref')
    affiliate_code = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to=upload_propic,
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field'
                              )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    def __str__(self):
        if self.affiliate_ref:
            return '{} < {}'.format(self.user.username, self.affiliate_ref.username)
        else:
            return self.user.username

    def aff_1_count(self):
        return self.user.up_ref.all().count()

    def aff_2_count(self):
        total = 0
        for affiliate in self.user.up_ref.all():
            total += affiliate.aff_1_count()

        return total

    def aff_3_count(self):
        total = 0
        for affiliate in self.user.up_ref.all():
            total += affiliate.aff_2_count()
        return total

    def get_url(self):
        domain = ALLOWED_HOSTS[0]

        return 'http://%s:8000/signup/%s' % (domain, self.user.id)

    def total_aff_count_2(self):
        total = 0
        total += self.aff_1_count()
        total += self.aff_2_count()
        return total

    def total_aff_count_3(self):
        total = 0
        total += self.aff_1_count()
        total += self.aff_2_count()
        total += self.aff_3_count()
        return total

    def up_comm(self): # How much commision user earns for immediate referer
        lv1 = 0
        lv2 = 0
        lv3 = 0
        for sale in self.user.affliliate_sale.all():
            lv1 += sale.affiliate_commission_1()

        for affiliate_2 in self.user.up_ref.all():
            for sale in affiliate_2.user.affliliate_sale.all():
                lv2 += sale.affiliate_commission_2()

            for affiliate_3 in affiliate_2.user.up_ref.all():
                for sale in affiliate_3.user.affliliate_sale.all():
                    lv3 += sale.affiliate_commission_3()

        return lv1 + lv2 + lv3


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)




@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.mobile_number = instance.username
    instance.profile.affiliate_code = instance.username
    instance.profile.save()


def save_profile(sender, instance, **kwargs):
    instance.user.full_name = instance.extra_data['name']
    # instance.user.profile.image = instance.get_avatar_url()
    instance.user.save()


post_save.connect(save_profile, sender=SocialAccount)


class ShippingDetails(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class ReceiptDetail(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone_number = models.CharField(max_length=50)
    ref = models.CharField(max_length=50)
    identifier = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20)


class Receipt(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payer = models.ForeignKey(ShippingDetails, on_delete=models.SET_NULL, null=True)
    receipt_detail = models.ForeignKey(ReceiptDetail, on_delete=models.SET_NULL, null=True)


class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    affiliate = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='affliliate_sale')
    shipping_details = models.ForeignKey(ShippingDetails, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    receipt = models.ForeignKey(Receipt, on_delete=models.SET_NULL, null=True)

    def affiliate_commission_0(self):
        total = 0
        for item in self.order.orderitem_set.all():
            comm = item.product.commission_category.affiliate_level_0 * item.product.price * item.quantity
            total += comm
        return total

    def affiliate_commission_1(self):
        total = 0
        for item in self.order.orderitem_set.all():
            comm = item.product.commission_category.affiliate_level_1 * item.product.price * item.quantity
            total += comm
        return total

    def affiliate_commission_2(self):
        total = 0
        for item in self.order.orderitem_set.all():
            comm = item.product.commission_category.affiliate_level_2 * item.product.price * item.quantity
            total += comm
        return total

    def affiliate_commission_3(self):
        total = 0
        for item in self.order.orderitem_set.all():
            comm = item.product.commission_category.affiliate_level_3 * item.product.price * item.quantity
            total += comm
        return total


class Delivery (models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    driver = models.CharField(max_length=50, blank=True)
    pickup_time = models.DateTimeField(blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20)


class Click(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # TODO consider adding account if there are multiple accounts


class Due(models.Model):
    recipient = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    narration = models.CharField(max_length=50)
    type = models.CharField(max_length=20)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, null=True, blank=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)



class Shop(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE)
    home_photo = models.ImageField(upload_to=upload_shopics,
                                   null=True,
                                   blank=True,
                                   width_field='width_field',
                                   height_field='height_field'
                                   )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    home_text = models.CharField(max_length=20, blank=True)
    top_three = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=50, blank=True)
    contact_address = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        try:
            image = Image.open(self.home_photo)
            current_aspect = self.width_field / self.height_field
            new_aspect = 4 / 3

            output = BytesIO()

            if current_aspect == new_aspect:
                pass
            elif current_aspect > new_aspect:
                rqw = new_aspect * self.height_field
                left = (self.width_field - rqw) / 2
                upper = 0
                right = left + rqw
                lower = self.height_field

                box = (left, upper, right, lower)
                new_image = image.crop(box)
                new_image.save(output, format='PNG', quality=100)
                output.seek(0)

                self.home_photo = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.home_photo.name.split('.')[0],
                                                       'image/jpeg', sys.getsizeof(output), None)

                super(Shop, self).save()
            else:
                rqh = (3 / 4) * self.width_field
                left = 0
                upper = (self.height_field - rqh) / 2
                right = self.width_field
                lower = left + rqh
                box = (left, upper, right, lower)
                new_image = image.crop(box)
                new_image.save(output, format='PNG', quality=100)
                output.seek(0)

                self.home_photo = InMemoryUploadedFile(output, 'ImageField', "%s.png" % self.home_photo.name.split('.')[0],
                                                       'image/jpeg', sys.getsizeof(output), None)

            super(Shop, self).save()
        except ValueError:
            super(Shop, self).save()


class Pin(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    pin = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)


class Banner(models.Model):
    head = models.CharField(max_length=30)
    head_color = models.CharField(max_length=20,
                                  default='primary',
                                  choices=(('primary', 'Red'),
                                           ('white', 'White'),
                                           ('black', 'Black')
                                           )
                                  )
    text = models.CharField(max_length=50)
    text_color = models.CharField(max_length=20,
                                  default='white',
                                  choices=(('primary', 'Red'),
                                           ('white', 'White'),
                                           ('black', 'Black')
                                           )
                                  )
    image = models.ImageField(upload_to=upload_banners,
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field'
                              )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)