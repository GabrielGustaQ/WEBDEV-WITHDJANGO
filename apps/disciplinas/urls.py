from django.urls import path

from . import views


urlpatterns = [
    path("", views.listar_disciplinas, name="disciplinas_list"),
    path("nova/", views.criar_disciplina, name="disciplinas_create"),
    path("<int:pk>/editar/", views.editar_disciplina, name="disciplinas_update"),
    path("<int:pk>/excluir/", views.excluir_disciplina, name="disciplinas_delete"),
]