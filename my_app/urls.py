from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login_user),
    path("logout/", views.logout_user),
    path("zipify/", views.zipify),
    path("zipify/<str:command>/", views.zipify),
    path("templates/", views.user_templates),
    path("my-drive/", views.drive_structure),
    path("my-drive/<str:command>/", views.drive_structure),
    path("trash/", views.trash),
    path("fonts/", views.fonts),
]
