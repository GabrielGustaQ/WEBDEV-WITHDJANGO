from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_alunos, name="alunos_list"),
    path("novo/", views.criar_aluno, name="alunos_create"),
    path("<int:pk>/editar/", views.editar_aluno, name="alunos_update"),
    path("<int:pk>/excluir/", views.excluir_aluno, name="alunos_delete"),
]