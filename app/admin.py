from django.contrib import admin
from .models import Cart, Customer, Product


# Register your models here.
@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "selling_price",
        "discounted_price",
        "description",
        "composition",
        "prodapp",
        "category",
        "product_image",
    ]


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "locality", "city", "mobile", "zipcode", "state"]


@admin.register(Cart)
class CartModeAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "quantity"]
