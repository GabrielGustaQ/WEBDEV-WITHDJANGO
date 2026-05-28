from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),

    path("", include("apps.accounts.urls")),
    path("alunos/", include("apps.alunos.urls")),
    path("disciplinas/", include("apps.disciplinas.urls")),
    path("matriculas/", include("apps.matriculas.urls")),
    path("relatorios/", include("apps.relatorios.urls")),
]