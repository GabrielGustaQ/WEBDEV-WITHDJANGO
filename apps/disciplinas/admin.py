from django.contrib import admin

from .models import Disciplina


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nome",
        "periodo_letivo",
        "carga_horaria",
        "vagas_total",
        "vagas_disponiveis",
        "ativa",
    )

    list_filter = (
        "ativa",
        "periodo_letivo",
    )

    search_fields = (
        "codigo",
        "nome",
        "periodo_letivo",
    )

    ordering = (
        "nome",
    )