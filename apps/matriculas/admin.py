from django.contrib import admin

from .models import Matricula


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ("aluno", "turma", "status", "criada_em")

    list_filter = ("status", "turma__periodo_letivo", "turma__disciplina")

    search_fields = (
        "aluno__nome",
        "aluno__matricula",
        "turma__disciplina__nome",
        "turma__disciplina__codigo",
        "turma__periodo_letivo",
    )

    ordering = ("-criada_em",)
