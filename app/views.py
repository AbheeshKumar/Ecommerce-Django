import os
import stat
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import stripe

from .forms import CustomerProfileForm, CustomerRegistrationForm
from .models import Cart, Customer, Order, Payment, Product

app_name = "app"


# Create your views here.
def home(req):
    return render(req, "app/home.html")


def about(req):
    return render(req, "app/about.html")


def contact(req):
    return render(req, "app/contact.html")


class CategoryView(View):
    def get(self, req, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values("title")
        return render(req, "app/category.html", locals())


class CategoryTitle(View):
    def get(self, req, val):
        product = Product.objects.filter(title=val)
        print(product[0].category)
        title = Product.objects.filter(category=product[0].category).values("title")
        return render(req, "app/category.html", locals())


class ProductDetail(View):
    def get(self, req, pk):
        product = Product.objects.get(pk=pk)
        return render(req, "app/productdetail.html", locals())


class CustomerRegistrationView(View):
    def get(self, req):
        form = CustomerRegistrationForm()
        return render(req, "app/cust_register.html", locals())

    def post(self, req):
        form = CustomerRegistrationForm(req.POST)
        if form.is_valid():
            form.save()
            messages.success(req, "Congratulations, You have registered successfully")
        else:
            messages.warning(req, "Invalid Input Data")
        return render(req, "app/cust_register.html", locals())


class ProfileView(View):
    def get(self, req):
        form = CustomerProfileForm()
        return render(req, "app/profile.html", locals())

    def post(self, req):
        form = CustomerProfileForm(req.POST)
        if form.is_valid():
            user = req.user
            name = form.cleaned_data["name"]
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            mobile = form.cleaned_data["mobile"]
            zipcode = form.cleaned_data["zipcode"]
            state = form.cleaned_data["state"]

            reg = Customer(
                user=user,
                name=name,
                locality=locality,
                city=city,
                mobile=mobile,
                zipcode=zipcode,
                state=state,
            )
            reg.save()
            messages.success(req, "Congratulations, Profile has been updated")
        else:
            messages.warning(req, "Error! Profile wasn't updated")

        return render(req, "app/profile.html", locals())


def address(req):
    add = Customer.objects.filter(user=req.user)
    return render(req, "app/address.html", locals())


class updateAddress(View):
    def get(self, req, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(req, "app/updateaddress.html", locals())

    def post(self, req, pk):
        form = CustomerProfileForm(req.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data["name"]
            add.locality = form.cleaned_data["locality"]
            add.city = form.cleaned_data["city"]
            add.mobile = form.cleaned_data["mobile"]
            add.state = form.cleaned_data["state"]
            add.zipcode = form.cleaned_data["zipcode"]
            add.save()
            messages.success("Customer has successfuly updated his information")
        else:
            messages.warning("Error Occured. Details were not updated")
        return redirect("app/address.html")


def add_to_cart(req):
    user = req.user
    prod_id = req.GET.get("prod_id")
    product = Product.objects.get(id=prod_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")


def show_cart(req):
    user = req.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for prod in cart:
        value = prod.quantity * prod.product.discounted_price
        amount += value
    totalamount = amount + 150
    return render(req, "app/addtocart.html", locals())


class Checkout(View):
    def get(self, req):
        user = req.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        amount = 0
        for prod in cart_items:
            value = prod.quantity * prod.product.discounted_price
            amount += value
        totalamount = amount + 150
        return render(req, "app/checkout.html", locals())


def plus_cart(req):
    if req.method == "GET":
        prod_id = req.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=req.user))
        c.quantity += 1
        c.save()
        user = req.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for prod in cart:
            value = prod.quantity * prod.product.discounted_price
            amount += value
        totalamount = amount + 150
        data = {"quantity": c.quantity, "amount": amount, "totalamount": totalamount}
        return JsonResponse(data)


def minus_cart(req):
    if req.method == "GET":
        user = req.user
        prod_id = req.GET.get("prod_id")
        c = Cart.objects.get(Q(product=prod_id) & Q(user=user))
        c.quantity -= 1
        c.save()
        cart = Cart.objects.filter(user=user)
        amount = 0
        for prod in cart:
            value = prod.quantity * prod.product.discounted_price
            amount += value
        totalamount = amount + 150
        data = {
            "quantity": c.quantity,
            "amount": amount,
            "totalamount": totalamount,
        }
        return JsonResponse(data)


def remove_item(req):
    if req.method == "GET":
        user = req.user
        prod_id = req.GET.get("prod_id")
        Cart.objects.get(Q(product=prod_id) & Q(user=user)).delete()
        cart = Cart.objects.filter(user=user)
        amount = 0
        for prod in cart:
            value = prod.quantity * prod.product.discounted_price
            amount += value
        totalamount = amount + 150
        data = {
            "amount": amount,
            "totalamount": totalamount,
        }
        return JsonResponse(data)


def create_checkout_session(req):
    user = req.user
    cust_id = req.GET.get("ad_id")
    base_url = (
        "https://ecommerce-django-production.up.railway.app/"
        if settings.DEBUG
        else "http://127.0.0.1:8000/"
    )
    print("Customer ID: ", cust_id)
    cart = Cart.objects.filter(user=user)
    list_items = []
    for item in cart:
        list_items.append(
            {
                "price_data": {
                    "currency": "pkr",
                    "product_data": {
                        "name": item.product.title,
                        "description": item.product.description,
                    },
                    "unit_amount": int(item.product.selling_price) * 100,
                },
                "quantity": item.quantity,
            }
        )
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            client_reference_id=user.id,
            line_items=list_items,
            mode="payment",
            success_url=base_url + "success",
            cancel_url=base_url + "cancel",
            currency="pkr",
            metadata={"cust_id": cust_id},
        )

    except Exception as e:
        return JsonResponse({"error": str(e)})

    return redirect(checkout_session.url, code=303)


@csrf_exempt
def payment_done(req):
    payload = req.body
    sig_header = req.META["HTTP_STRIPE_SIGNATURE"]
    endpoint_secret = (
        os.getenv("STRIPE_WEBHOOK_SECRET_LOCAL")
        if settings.DEBUG
        else os.getenv("STRIPE_WEBHOOK_SECRET_PROD")
    )
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        fullfill_order(session)

    return JsonResponse({"status": "success"}, status=200)


def fullfill_order(session):
    user_id = session.get("client_reference_id")
    amount_total = session.get("amount_total")
    payment_status = session.get("payment_status")
    stripe_order_id = session.get("id")
    stripe_payment_id = session.get("payment_intent")
    cust_id = session.get("metadata").get("cust_id")
    user = User.objects.get(id=user_id)
    cart = Cart.objects.filter(user=user)
    payment = Payment.objects.create(
        user=user,
        amount=amount_total,
        stripe_order_id=stripe_order_id,
        stripe_payment_id=stripe_payment_id,
        stripe_payment_status=payment_status,
        paid=True if payment_status == True else False,
    )

    payment.save()
    print("Payment", payment)
    customer = Customer.objects.get(id=cust_id)
    for item in cart:
        order = Order.objects.create(
            user=user,
            customer=customer,
            product=item.product,
            quantity=item.quantity,
            payment=payment,
        )
        order.save()
        print("Order", order)


def success(req):
    return render(req, "app/success.html")


def cancel(req):
    return render(req, "app/cancel.html")
