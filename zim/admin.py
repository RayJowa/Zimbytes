from django.contrib import admin

from .models import AttributeValue, Order, OrderItem, Product, ProductAttribute, ProductImage, Profile


class ImageInline(admin.StackedInline):
    model = ProductImage
    extra = 5


class AttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 2


class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline, AttributeInline]


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 3


class AttributeAdmin(admin.ModelAdmin):
    inlines = [AttributeValueInline, ]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 2


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, ]


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, AttributeAdmin)
admin.site.register(Profile)
