from django.contrib import admin
from .models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "matricula",
        "email",
        "curso",
        "ativo",
    )

    list_filter = (
        "ativo",
        "curso",
    )

    search_fields = (
        "nome",
        "matricula",
        "email",
        "curso",
    )

    ordering = (
        "nome",
    )