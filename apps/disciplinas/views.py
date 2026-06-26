from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.views import usuario_secretaria

from .forms import DisciplinaForm, TurmaForm
from .models import Disciplina, Turma


@login_required
@user_passes_test(usuario_secretaria)
def listar_disciplinas(request):
    busca = request.GET.get("q", "")

    disciplinas = Disciplina.objects.all()

    if busca:
        disciplinas = disciplinas.filter(
            Q(nome__icontains=busca) | Q(codigo__icontains=busca)
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
        form = DisciplinaForm()

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
        if disciplina.turmas.exists():
            messages.error(
                request,
                "Não é possível excluir esta disciplina pois ela possui turmas vinculadas."
            )
        else:
            disciplina.delete()
            messages.success(request, "Disciplina excluída com sucesso.")

        return redirect("disciplinas_list")

    return render(request, "disciplinas/confirm_delete.html", {
        "disciplina": disciplina,
    })


# ── Turmas ──────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(usuario_secretaria)
def listar_turmas(request):
    busca = request.GET.get("q", "")

    turmas = Turma.objects.select_related("disciplina").all()

    if busca:
        turmas = turmas.filter(
            Q(disciplina__nome__icontains=busca)
            | Q(disciplina__codigo__icontains=busca)
            | Q(periodo_letivo__icontains=busca)
        )

    return render(request, "turmas/list.html", {
        "turmas": turmas,
        "busca": busca,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def criar_turma(request):
    if request.method == "POST":
        form = TurmaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Turma cadastrada com sucesso.")
            return redirect("turmas_list")
    else:
        form = TurmaForm(initial={"ativa": True})

    return render(request, "turmas/form.html", {
        "form": form,
        "turma": None,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def editar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)

    if request.method == "POST":
        form = TurmaForm(request.POST, instance=turma)

        if form.is_valid():
            form.save()
            messages.success(request, "Turma atualizada com sucesso.")
            return redirect("turmas_list")
    else:
        form = TurmaForm(instance=turma)

    return render(request, "turmas/form.html", {
        "form": form,
        "turma": turma,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def excluir_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)

    if request.method == "POST":
        if turma.matriculas.exists():
            turma.ativa = False
            turma.save(update_fields=["ativa"])
            messages.success(request, "Turma inativada porque possui matrículas vinculadas.")
        else:
            turma.delete()
            messages.success(request, "Turma excluída com sucesso.")

        return redirect("turmas_list")

    return render(request, "turmas/confirm_delete.html", {
        "turma": turma,
    })
