from django.urls import path

from . import views

urlpatterns = [
    path("index/", views.index),
    path("login/", views.login_user),
    path("logout/", views.logout_user),
    path("certify/", views.certify_document),
]
