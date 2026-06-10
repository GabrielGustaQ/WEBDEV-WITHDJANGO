from django.urls import path

from . import views


urlpatterns = [
    path("", views.listar_matriculas, name="matriculas_list"),
    path("nova/", views.nova_matricula, name="matriculas_create"),
    path("<int:pk>/cancelar/", views.cancelar, name="matriculas_cancelar"),
    path("minhas/", views.minhas_matriculas, name="minhas_matriculas"),
]