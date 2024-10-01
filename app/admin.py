from django.contrib import admin
from .models import Cart, Customer, Order, Payment, Product


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


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "amount",
        "stripe_order_id",
        "stripe_payment_status",
        "stripe_payment_id",
        "paid",
    ]


@admin.register(Order)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "customer",
        "product",
        "quantity",
        "ordered_date",
        "status",
        "payment",
    ]
