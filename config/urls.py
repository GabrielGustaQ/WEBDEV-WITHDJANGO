from django.contrib import admin
from django.urls import path, include

from apps.disciplinas.urls import turma_urlpatterns


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("apps.accounts.urls")),

    path("alunos/", include("apps.alunos.urls")),
    path("disciplinas/", include("apps.disciplinas.urls")),
    path("turmas/", include((turma_urlpatterns, ""))),
    path("matriculas/", include("apps.matriculas.urls")),
    path("relatorios/", include("apps.relatorios.urls")),
]
