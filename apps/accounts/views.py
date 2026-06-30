from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, TrocaSenhaInicialForm
from .models import PerfilUsuario


def obter_ou_criar_perfil(user):
    if hasattr(user, "perfil"):
        return user.perfil

    if user.is_superuser or user.is_staff or user.groups.filter(name="Secretaria").exists():
        tipo = PerfilUsuario.Tipo.SECRETARIA
    else:
        tipo = PerfilUsuario.Tipo.ALUNO

    perfil, _ = PerfilUsuario.objects.get_or_create(
        user=user,
        defaults={
            "tipo": tipo,
            "senha_temporaria": False,
        }
    )

    return perfil


def redirecionar_usuario(user):
    perfil = obter_ou_criar_perfil(user)

    if perfil.senha_temporaria:
        return "trocar_senha_primeiro_acesso"

    return "dashboard"


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return redirect("login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect(redirecionar_usuario(request.user))

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            perfil = obter_ou_criar_perfil(user)

            if perfil.senha_temporaria:
                messages.info(request, "Altere sua senha temporária para continuar.")
                return redirect("trocar_senha_primeiro_acesso")

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect(redirecionar_usuario(user))
    else:
        form = LoginForm()

    return render(request, "login.html", {
        "form": form,
    })


def logout_view(request):
    auth_logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    perfil = obter_ou_criar_perfil(request.user)
    context = {"perfil": perfil}

    if perfil.is_aluno and hasattr(request.user, "aluno"):
        from apps.matriculas.models import Matricula
        aluno = request.user.aluno
        matriculas = Matricula.objects.filter(aluno=aluno)
        context["total_matriculas"] = matriculas.count()
        context["confirmadas"] = matriculas.filter(status=Matricula.STATUS_CONFIRMADA).count()
        context["pendentes"] = matriculas.filter(status=Matricula.STATUS_PENDENTE).count()

    return render(request, "dashboard.html", context)


@login_required
def trocar_senha_primeiro_acesso(request):
    perfil = obter_ou_criar_perfil(request.user)

    if not perfil.senha_temporaria:
        return redirect("dashboard")

    if request.method == "POST":
        form = TrocaSenhaInicialForm(request.POST, user=request.user)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(request, "Senha alterada com sucesso.")
            return redirect("dashboard")
    else:
        form = TrocaSenhaInicialForm(user=request.user)

    return render(request, "accounts/trocar_senha.html", {
        "form": form,
    })


def usuario_secretaria(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or user.groups.filter(name="Secretaria").exists()
            or (
                hasattr(user, "perfil")
                and user.perfil.tipo == PerfilUsuario.Tipo.SECRETARIA
            )
        )
    )


def usuario_aluno(user):
    return (
        user.is_authenticated
        and hasattr(user, "perfil")
        and user.perfil.tipo == PerfilUsuario.Tipo.ALUNO
    )