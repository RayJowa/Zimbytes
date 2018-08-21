from django.contrib import admin

from .models import Banner, AttributeValue, Category, Click, Due, CommissionCategory, Order, OrderItem, Payment, Product, ProductAttribute, \
    ProductImage, Profile, Receipt, ReceiptDetail, ShippingDetails, Sale, SubCategory


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


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 3


class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline, ]


admin.site.register(Banner)
admin.site.register(Click)
admin.site.register(Due)
admin.site.register(CommissionCategory)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, AttributeAdmin)
admin.site.register(Profile)
admin.site.register(Receipt)
admin.site.register(ReceiptDetail)
admin.site.register(Sale)
admin.site.register(ShippingDetails)
