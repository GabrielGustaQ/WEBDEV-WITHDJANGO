from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404

from apps.accounts.views import usuario_secretaria
from apps.disciplinas.models import Turma

from .forms import MatriculaForm
from .models import Matricula
from .services import realizar_matricula, cancelar_matricula


@login_required
@user_passes_test(usuario_secretaria)
def listar_matriculas(request):
    matriculas = Matricula.objects.select_related(
        "aluno",
        "turma",
        "turma__disciplina",
    ).all()

    return render(request, "matriculas/list.html", {
        "matriculas": matriculas,
    })


@login_required
@user_passes_test(usuario_secretaria)
def nova_matricula(request):
    if request.method == "POST":
        form = MatriculaForm(request.POST)

        if form.is_valid():
            aluno = form.cleaned_data["aluno"]
            turma = form.cleaned_data["turma"]

            try:
                realizar_matricula(aluno, turma)
                messages.success(request, "Pré-matrícula realizada com sucesso.")
                return redirect("matriculas_list")
            except ValueError as erro:
                messages.error(request, str(erro))
    else:
        form = MatriculaForm()

    return render(request, "matriculas/form.html", {
        "form": form,
    })


@login_required
@user_passes_test(usuario_secretaria)
def cancelar(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)

    try:
        cancelar_matricula(matricula)
        messages.success(request, "Pré-matrícula cancelada com sucesso.")
    except ValueError as erro:
        messages.error(request, str(erro))

    return redirect("matriculas_list")


@login_required
def matricular_aluno(request):
    if not hasattr(request.user, "aluno"):
        messages.error(request, "Usuário não possui perfil de aluno.")
        return redirect("dashboard")

    aluno = request.user.aluno

    if request.method == "POST":
        turma_id = request.POST.get("turma_id")
        turma = get_object_or_404(Turma, pk=turma_id)
        try:
            realizar_matricula(aluno, turma)
            messages.success(request, f"Matrícula em {turma.disciplina.nome} realizada com sucesso.")
        except ValueError as erro:
            messages.error(request, str(erro))
        return redirect("matriculas_matricular")

    turmas_ativas = Matricula.objects.filter(
        aluno=aluno,
    ).exclude(status=Matricula.STATUS_CANCELADA).values_list("turma_id", flat=True)

    turmas = Turma.objects.filter(
        ativa=True,
        vagas_disponiveis__gt=0,
    ).exclude(
        pk__in=turmas_ativas,
    ).select_related("disciplina").order_by("-vagas_disponiveis", "disciplina__nome", "periodo_letivo")

    periodo = request.GET.get("periodo", "")
    busca = request.GET.get("q", "")

    if periodo:
        turmas = turmas.filter(periodo_letivo__icontains=periodo)
    if busca:
        turmas = turmas.filter(disciplina__nome__icontains=busca) | turmas.filter(disciplina__codigo__icontains=busca)

    return render(request, "matriculas/matricular.html", {
        "turmas": turmas,
        "periodo": periodo,
        "busca": busca,
    })


@login_required
def minhas_matriculas(request):
    if not hasattr(request.user, "aluno"):
        messages.error(request, "Usuário não possui perfil de aluno.")
        return redirect("dashboard")

    matriculas = Matricula.objects.select_related(
        "turma",
        "turma__disciplina",
    ).filter(
        aluno=request.user.aluno,
    )

    return render(request, "matriculas/list.html", {
        "matriculas": matriculas,
        "is_aluno_view": True,
    })
