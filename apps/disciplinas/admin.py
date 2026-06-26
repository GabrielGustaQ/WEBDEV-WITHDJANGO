from django.contrib import admin

from .models import Disciplina, Turma


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "carga_horaria")

    search_fields = ("codigo", "nome")

    ordering = ("nome",)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = (
        "disciplina",
        "periodo_letivo",
        "vagas_total",
        "vagas_disponiveis",
        "ativa",
    )

    list_filter = ("ativa", "periodo_letivo", "disciplina")

    search_fields = (
        "disciplina__codigo",
        "disciplina__nome",
        "periodo_letivo",
    )

    ordering = ("disciplina__nome", "periodo_letivo")
