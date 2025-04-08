from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.user_dashboard, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("user-list/", views.user_list, name="user-list"),
    path("verify/<uidb64>/<token>/", views.verify_email, name="verify-email"),
#     path("reset-password/", views.reset_password, name="password-reset"),
#     path(
#         "reset-password-confirm/<uidb64>/<token>/",
#         views.reset_password_confirm,
#         name="password_reset_confirm",
#     ),
#     path("set-new-password/", views.set_new_password, name="new-password"),
]