from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from app.models import Customer
from . import views
from .forms import (
    CustomerLoginForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
)
from django.contrib.auth import views as auth_view

urlpatterns = [
    # Information
    path("", views.home),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    # Products
    path("category/<slug:val>", views.CategoryView.as_view(), name="category"),
    path(
        "product-detail/<int:pk>", views.ProductDetail.as_view(), name="product-detail"
    ),
    path("category-title/<val>", views.CategoryTitle.as_view(), name="category-title"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("address/", views.address, name="address"),
    path("updateAddress/<int:pk>", views.updateAddress.as_view(), name="updateAddress"),
    # Authentication
    path(
        "register/", views.CustomerRegistrationView.as_view(), name="customer-register"
    ),
    path(
        "accounts/login",
        auth_view.LoginView.as_view(
            template_name="app/login.html", authentication_form=CustomerLoginForm
        ),
        name="login",
    ),
    path(
        "password-change/",
        auth_view.PasswordChangeView.as_view(
            template_name="app/password-change.html",
            form_class=MyPasswordChangeForm,
            success_url="/password-change-done",
        ),
        name="password-change",
    ),
    path(
        "password-change-done/",
        auth_view.PasswordChangeDoneView.as_view(
            template_name="app/password-change-done.html",
        ),
        name="password-change-done",
    ),
    path("logout/", auth_view.LogoutView.as_view(next_page="login"), name="logout"),
    path(
        "password-reset/",
        auth_view.PasswordResetView.as_view(
            template_name="app/password-reset.html",
            form_class=MyPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password-reset-done",
        auth_view.PasswordResetDoneView.as_view(
            template_name="app/password-reset-done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_view.PasswordResetConfirmView.as_view(
            template_name="app/password-reset-confirm.html",
            form_class=MySetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete",
        auth_view.PasswordResetCompleteView.as_view(
            template_name="app/password-reset-complete.html"
        ),
        name="password_reset_complete",
    ),
    # Cart
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("cart/", views.show_cart, name="show-cart"),
    path("checkout/", views.Checkout.as_view(), name="checkout"),
    path("pluscart/", views.plus_cart),
    path("minuscart/", views.minus_cart),
    path("removeitem/", views.remove_item),
    path("stripe-checkout/", views.create_checkout_session, name="stripe-checkout"),
    path("success/", views.success),
    path("cancel/", views.cancel),
    path("payment-done/", views.payment_done, name="payment done"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
