from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver


def upload_location(instance, filename):
    return 'images/%s/%s' % (instance.product.id, filename)


class Product(models.Model):
    supplier = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field'
                              )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product)
    attribute = models.CharField(max_length=20)

    def __str__(self):
        return self.product.name + ' ' + self.attribute


class AttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute)
    value = models.CharField(max_length=20)


class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    session = models.ForeignKey(Session, blank=True, null=True)
    last_modifies = models.DateTimeField(auto_now=True)

    def order_total(self):
        total = 0

        for item in self.orderitem_set.all():
            total += item.quantity * item.product.price

        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()

    def item_total(self):
        return self.product.price * self.quantity


class OrderItemAttribute(models.Model):
    models.ForeignKey(OrderItem)
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
    mobile_number = models.TextField(max_length=25, blank=True)
    user_type = models.CharField(default='client',
                                 max_length=20,
                                 blank=True,
                                 choices=(
                                     ('client', 'client'),
                                     ('supplier', 'supplier'),
                                     ('affiliate', 'affiliate')
                                 )
                                 )
    banking_details = models.ForeignKey(BankingDetails, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    town = models.CharField(max_length=30, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

