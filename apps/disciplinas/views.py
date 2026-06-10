from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.views import usuario_secretaria

from .forms import DisciplinaForm
from .models import Disciplina


@login_required
@user_passes_test(usuario_secretaria)
def listar_disciplinas(request):
    busca = request.GET.get("q", "")

    disciplinas = Disciplina.objects.all()

    if busca:
        disciplinas = disciplinas.filter(
            Q(nome__icontains=busca)
            | Q(codigo__icontains=busca)
            | Q(periodo_letivo__icontains=busca)
        )

    return render(request, "disciplinas/list.html", {
        "disciplinas": disciplinas,
        "busca": busca,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def criar_disciplina(request):
    if request.method == "POST":
        form = DisciplinaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Disciplina cadastrada com sucesso.")
            return redirect("disciplinas_list")
    else:
        form = DisciplinaForm(initial={
            "ativa": True,
        })

    return render(request, "disciplinas/form.html", {
        "form": form,
        "disciplina": None,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)

    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)

        if form.is_valid():
            form.save()
            messages.success(request, "Disciplina atualizada com sucesso.")
            return redirect("disciplinas_list")
    else:
        form = DisciplinaForm(instance=disciplina)

    return render(request, "disciplinas/form.html", {
        "form": form,
        "disciplina": disciplina,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def excluir_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)

    if request.method == "POST":
        if disciplina.matriculas.exists():
            disciplina.ativa = False
            disciplina.save(update_fields=["ativa"])
            messages.success(request, "Disciplina inativada porque possui matrículas vinculadas.")
        else:
            disciplina.delete()
            messages.success(request, "Disciplina excluída com sucesso.")

        return redirect("disciplinas_list")

    return render(request, "disciplinas/confirm_delete.html", {
        "disciplina": disciplina,
    })