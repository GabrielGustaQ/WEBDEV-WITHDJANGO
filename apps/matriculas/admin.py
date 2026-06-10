from django.contrib import admin

from .models import Matricula


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = (
        "aluno",
        "disciplina",
        "periodo_letivo",
        "status",
        "criada_em",
    )

    list_filter = (
        "status",
        "periodo_letivo",
        "disciplina",
    )

    search_fields = (
        "aluno__nome",
        "aluno__matricula",
        "disciplina__nome",
        "disciplina__codigo",
        "periodo_letivo",
    )

    ordering = (
        "-criada_em",
    )