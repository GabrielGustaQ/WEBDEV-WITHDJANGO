from django.urls import path

from . import views


urlpatterns = [
    path(
        "matriculas-por-disciplina/",
        views.matriculas_por_disciplina,
        name="relatorio_matriculas_por_disciplina",
    ),
    path(
        "disciplinas-com-vagas/",
        views.disciplinas_com_vagas,
        name="relatorio_disciplinas_com_vagas",
    ),
    path(
        "historico-aluno/",
        views.historico_aluno,
        name="relatorio_historico_aluno",
    ),
    path(
        "vagas/",
        views.disciplinas_com_vagas_aluno,
        name="relatorio_vagas_aluno",
    ),
    path(
        "meu-historico/",
        views.meu_historico,
        name="relatorio_meu_historico",
    ),
]
