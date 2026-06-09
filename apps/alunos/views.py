from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AlunoForm
from .models import Aluno


def usuario_secretaria(user):
    return user.is_superuser or user.groups.filter(name="Secretaria").exists()


@login_required
@user_passes_test(usuario_secretaria)
def listar_alunos(request):
    busca = request.GET.get("q", "")

    alunos = Aluno.objects.select_related("user").all()

    if busca:
        alunos = alunos.filter(
            Q(nome__icontains=busca) |
            Q(matricula__icontains=busca) |
            Q(email__icontains=busca) |
            Q(curso__icontains=busca)
        )

    return render(request, "alunos/list.html", {
        "alunos": alunos,
        "busca": busca,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def criar_aluno(request):
    if request.method == "POST":
        form = AlunoForm(request.POST)

        if form.is_valid():
            aluno = form.save(commit=False)

            if User.objects.filter(username=aluno.matricula).exists():
                messages.error(request, "Já existe um usuário com essa matrícula.")
                return render(request, "alunos/form.html", {
                    "form": form,
                    "aluno": None,
                })

            grupo_aluno, _ = Group.objects.get_or_create(name="Aluno")

            user = User.objects.create_user(
                username=aluno.matricula,
                email=aluno.email,
                password="aluno123",
                first_name=aluno.nome,
            )

            user.groups.add(grupo_aluno)

            aluno.user = user
            aluno.save()

            messages.success(
                request,
                "Aluno cadastrado com sucesso. Senha inicial: aluno123"
            )
            return redirect("alunos_list")
    else:
        form = AlunoForm()

    return render(request, "alunos/form.html", {
        "form": form,
        "aluno": None,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def editar_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        form = AlunoForm(request.POST, instance=aluno)

        if form.is_valid():
            aluno_editado = form.save(commit=False)

            usuario_com_mesma_matricula = User.objects.filter(
                username=aluno_editado.matricula
            ).exclude(
                pk=aluno.user.pk
            ).exists()

            if usuario_com_mesma_matricula:
                messages.error(request, "Já existe um usuário com essa matrícula.")
                return render(request, "alunos/form.html", {
                    "form": form,
                    "aluno": aluno,
                })

            aluno_editado.save()

            aluno.user.username = aluno_editado.matricula
            aluno.user.email = aluno_editado.email
            aluno.user.first_name = aluno_editado.nome
            aluno.user.is_active = aluno_editado.ativo
            aluno.user.save()

            messages.success(request, "Aluno atualizado com sucesso.")
            return redirect("alunos_list")
    else:
        form = AlunoForm(instance=aluno)

    return render(request, "alunos/form.html", {
        "form": form,
        "aluno": aluno,
    })


@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        aluno.ativo = False
        aluno.save(update_fields=["ativo"])

        aluno.user.is_active = False
        aluno.user.save(update_fields=["is_active"])

        messages.success(request, "Aluno inativado com sucesso.")
        return redirect("alunos_list")

    return render(request, "alunos/confirm_delete.html", {
        "aluno": aluno,
    })