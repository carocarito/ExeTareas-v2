from django.urls import path
from . import views

urlpatterns = [
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("service-worker.js", views.service_worker, name="service_worker"),
    path("pwa/icon-<int:size>.svg", views.pwa_icon, name="pwa_icon"),
    path("", views.dashboard, name="dashboard"),
    path("categorias/", views.categories, name="categories"),
    path("nueva/<str:category>/", views.task_create, name="task_create"),
    path("editar/<int:pk>/", views.task_edit, name="task_edit"),
    path("calendario/", views.calendar_view, name="calendar"),
    path("completar/<int:pk>/", views.toggle_completion, name="toggle_completion"),
]
