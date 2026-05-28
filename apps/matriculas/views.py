from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404

from .forms import MatriculaForm
from .models import Matricula
from .services import realizar_matricula, cancelar_matricula


def usuario_secretaria(user):
    return user.is_superuser or user.groups.filter(name="Secretaria").exists()


@login_required
@user_passes_test(usuario_secretaria)
def listar_matriculas(request):
    matriculas = Matricula.objects.select_related(
        "aluno",
        "disciplina"
    ).all()

    return render(request, "matriculas/list.html", {
        "matriculas": matriculas
    })


@login_required
@user_passes_test(usuario_secretaria)
def nova_matricula(request):
    if request.method == "POST":
        form = MatriculaForm(request.POST)

        if form.is_valid():
            aluno = form.cleaned_data["aluno"]
            disciplina = form.cleaned_data["disciplina"]

            try:
                realizar_matricula(aluno, disciplina)
                messages.success(request, "Pré-matrícula realizada com sucesso.")
                return redirect("matriculas_list")
            except ValueError as erro:
                messages.error(request, str(erro))
    else:
        form = MatriculaForm()

    return render(request, "matriculas/form.html", {
        "form": form
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
def minhas_matriculas(request):
    if not hasattr(request.user, "aluno"):
        messages.error(request, "Usuário não possui perfil de aluno.")
        return redirect("dashboard")

    matriculas = Matricula.objects.select_related(
        "disciplina"
    ).filter(
        aluno=request.user.aluno
    )

    return render(request, "matriculas/list.html", {
        "matriculas": matriculas
    })