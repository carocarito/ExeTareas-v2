from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from tasks import views as task_views

urlpatterns = [path("admin/", admin.site.urls), path("login/", auth_views.LoginView.as_view(template_name="tasks/login.html"), name="login"), path("registro/", task_views.register, name="register"), path("invitado/", task_views.guest_login, name="guest_login"), path("salir/", task_views.logout_view, name="logout"), path("", include("tasks.urls"))]
