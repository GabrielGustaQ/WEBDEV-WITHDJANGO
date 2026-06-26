from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render

from apps.accounts.views import usuario_secretaria
from apps.alunos.models import Aluno
from apps.disciplinas.models import Turma
from apps.matriculas.models import Matricula


@login_required
@user_passes_test(usuario_secretaria)
def matriculas_por_disciplina(request):
    disciplina_busca = request.GET.get("disciplina", "")
    periodo = request.GET.get("periodo", "")

    matriculas = Matricula.objects.select_related(
        "aluno",
        "turma",
        "turma__disciplina",
    ).all()

    if disciplina_busca:
        matriculas = matriculas.filter(
            Q(turma__disciplina__nome__icontains=disciplina_busca)
            | Q(turma__disciplina__codigo__icontains=disciplina_busca)
        )

    if periodo:
        matriculas = matriculas.filter(
            turma__periodo_letivo__icontains=periodo
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

    turmas = Turma.objects.filter(
        ativa=True,
    ).select_related("disciplina").order_by("vagas_disponiveis", "disciplina__nome", "periodo_letivo")

    if periodo:
        turmas = turmas.filter(periodo_letivo__icontains=periodo)

    return render(request, "relatorios/disciplinas_com_vagas.html", {
        "turmas": turmas,
        "periodo": periodo,
    })


@login_required
def disciplinas_com_vagas_aluno(request):
    periodo = request.GET.get("periodo", "")

    turmas = Turma.objects.filter(
        ativa=True,
        vagas_disponiveis__gt=0,
    ).select_related("disciplina").order_by("-vagas_disponiveis", "disciplina__nome", "periodo_letivo")

    if periodo:
        turmas = turmas.filter(periodo_letivo__icontains=periodo)

    return render(request, "relatorios/disciplinas_com_vagas.html", {
        "turmas": turmas,
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
                "turma",
                "turma__disciplina",
            ).filter(
                aluno=aluno,
            )

    return render(request, "relatorios/historico_aluno.html", {
        "aluno": aluno,
        "matriculas": matriculas,
        "aluno_busca": aluno_busca,
    })


@login_required
def meu_historico(request):
    if not hasattr(request.user, "aluno"):
        messages.error(request, "Usuário não possui perfil de aluno.")
        return redirect("dashboard")

    aluno = request.user.aluno
    matriculas = Matricula.objects.select_related(
        "turma",
        "turma__disciplina",
    ).filter(aluno=aluno)

    return render(request, "relatorios/meu_historico.html", {
        "aluno": aluno,
        "matriculas": matriculas,
    })
