# =============================================================================
# URLS.PY — Roteamento de URLs do app "alunos"
#
# Este arquivo mapeia endereços (URLs) para funções (views).
# Quando o usuário acessa "/alunos/novo/", o Django consulta essa lista
# e executa a view correspondente.
#
# Este arquivo é incluído pelo urls.py principal do projeto,
# geralmente com um prefixo como: path("alunos/", include("apps.alunos.urls"))
# =============================================================================

from django.urls import path
from . import views  # Importa as views deste mesmo app


urlpatterns = [
    # "" → /alunos/          | Lista todos os alunos cadastrados
    # name= permite referenciar esta URL pelo nome em vez do caminho literal,
    # usando {% url 'alunos_list' %} nos templates ou redirect("alunos_list") nas views.
    path("", views.listar_alunos, name="alunos_list"),

    # "novo/" → /alunos/novo/   | Exibe o formulário de cadastro de novo aluno
    path("novo/", views.criar_aluno, name="alunos_create"),

    # "<int:pk>/editar/" → /alunos/3/editar/
    # <int:pk> é um parâmetro dinâmico: captura um número inteiro da URL
    # e o passa para a view como o argumento 'pk' (primary key = ID do aluno).
    path("<int:pk>/editar/", views.editar_aluno, name="alunos_update"),

    # "<int:pk>/excluir/" → /alunos/3/excluir/
    # Mesma lógica: o ID do aluno é capturado diretamente da URL.
    path("<int:pk>/excluir/", views.excluir_aluno, name="alunos_delete"),
]