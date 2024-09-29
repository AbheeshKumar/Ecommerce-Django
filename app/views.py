from threading import local
from django.contrib import messages
from django.db.models import Q, Count
from unicodedata import category
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import CustomerProfileForm, CustomerRegistrationForm
from .models import Cart, Customer, Product

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
        form = CustomerRegistrationForm(req.POST, req.FILES)
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
