from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render

from apps.accounts.views import usuario_secretaria
from apps.alunos.models import Aluno
from apps.disciplinas.models import Disciplina
from apps.matriculas.models import Matricula


@login_required
@user_passes_test(usuario_secretaria)
def matriculas_por_disciplina(request):
    disciplina_busca = request.GET.get("disciplina", "")
    periodo = request.GET.get("periodo", "")

    matriculas = Matricula.objects.select_related(
        "aluno",
        "disciplina",
    ).all()

    if disciplina_busca:
        matriculas = matriculas.filter(
            Q(disciplina__nome__icontains=disciplina_busca)
            | Q(disciplina__codigo__icontains=disciplina_busca)
        )

    if periodo:
        matriculas = matriculas.filter(
            periodo_letivo__icontains=periodo
        )

    return render(request, "relatorios/matriculas_por_disciplina.html", {
        "matriculas": matriculas,
        "disciplina_busca": disciplina_busca,
        "periodo": periodo,
    })


@login_required
@user_passes_test(usuario_secretaria)
def disciplinas_com_vagas(request):
    periodo = request.GET.get("periodo", "")

    disciplinas = Disciplina.objects.filter(
        ativa=True
    ).order_by("nome")

    if periodo:
        disciplinas = disciplinas.filter(
            periodo_letivo__icontains=periodo
        )

    return render(request, "relatorios/disciplinas_com_vagas.html", {
        "disciplinas": disciplinas,
        "periodo": periodo,
    })


@login_required
@user_passes_test(usuario_secretaria)
def historico_aluno(request):
    aluno_busca = request.GET.get("aluno", "")

    aluno = None
    matriculas = Matricula.objects.none()

    if aluno_busca:
        aluno = Aluno.objects.filter(
            Q(nome__icontains=aluno_busca)
            | Q(matricula__icontains=aluno_busca)
        ).first()

        if aluno:
            matriculas = Matricula.objects.select_related(
                "disciplina",
            ).filter(
                aluno=aluno,
            )

    return render(request, "relatorios/historico_aluno.html", {
        "aluno": aluno,
        "matriculas": matriculas,
        "aluno_busca": aluno_busca,
    })