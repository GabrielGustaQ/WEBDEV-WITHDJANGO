# =============================================================================
# VIEWS.PY — A "Camada de Lógica" do Django (V do padrão MTV)
#
# Uma view é uma função Python que recebe uma requisição HTTP (request)
# e retorna uma resposta HTTP (uma página HTML, um redirect, etc.).
#
# Fluxo básico de uma requisição no Django:
#   URL → urls.py → view (aqui) → template → resposta ao navegador
# =============================================================================

# Sistema de mensagens flash: exibe alertas de sucesso/erro para o usuário.
from django.contrib import messages

# Decoradores de autenticação: protegem views de acesso não autorizado.
from django.contrib.auth.decorators import login_required, user_passes_test

# User e Group são modelos embutidos do Django para autenticação e permissões.
from django.contrib.auth.models import User, Group

# transaction.atomic garante que um conjunto de operações no banco
# seja executado de forma "tudo ou nada" — se algo falhar, nada é salvo.
from django.db import transaction

# Q permite construir filtros complexos com operadores OR (|) e AND (&).
from django.db.models import Q

# render → renderiza um template HTML e retorna como resposta.
# redirect → redireciona o navegador para outra URL.
# get_object_or_404 → busca um objeto no banco; se não existir, retorna erro 404.
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.models import PerfilUsuario

from .forms import AlunoForm
from .models import Aluno


# =============================================================================
# FUNÇÃO AUXILIAR DE PERMISSÃO
# Retorna True se o usuário pode acessar as views de secretaria.
# Usada pelo decorador @user_passes_test abaixo.
# =============================================================================
def usuario_secretaria(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser          # Superusuário tem acesso total
            or user.is_staff           # Staff também tem acesso
            or user.groups.filter(name="Secretaria").exists()  # Grupo de secretaria
            or (
                hasattr(user, "perfil")
                and user.perfil.tipo == PerfilUsuario.Tipo.SECRETARIA
            )
        )
    )


# =============================================================================
# VIEW: LISTAR ALUNOS
# =============================================================================

# @login_required → redireciona para a página de login se o usuário não estiver autenticado.
@login_required
# @user_passes_test → executa a função 'usuario_secretaria'; se retornar False, acesso negado.
@user_passes_test(usuario_secretaria)
def listar_alunos(request):
    # request.GET contém os parâmetros da URL (ex: /alunos/?q=joao).
    # .get("q", "") retorna o valor de "q" ou string vazia se não existir.
    busca = request.GET.get("q", "")

    # ORM do Django: Aluno.objects.all() equivale a "SELECT * FROM aluno".
    # select_related("user") faz um JOIN com a tabela User em uma única query (otimização).
    alunos = Aluno.objects.select_related("user").all()

    if busca:
        # Q permite filtrar por múltiplos campos ao mesmo tempo usando OR (|).
        # __icontains → LIKE '%valor%' no SQL, sem diferenciar maiúsculas/minúsculas.
        alunos = alunos.filter(
            Q(nome__icontains=busca)
            | Q(matricula__icontains=busca)
            | Q(email__icontains=busca)
            | Q(curso__icontains=busca)
        )

    # render() carrega o template e passa os dados como dicionário (contexto).
    # No template, {{ alunos }} e {{ busca }} ficam disponíveis para exibição.
    return render(request, "alunos/list.html", {
        "alunos": alunos,
        "busca": busca,
    })


# =============================================================================
# VIEW: CRIAR ALUNO
# =============================================================================

@login_required
@user_passes_test(usuario_secretaria)
# @transaction.atomic → se qualquer linha abaixo falhar, o banco reverte tudo.
# Isso garante que não criemos um User sem o Aluno correspondente, ou vice-versa.
@transaction.atomic
def criar_aluno(request):
    # O mesmo endpoint responde a GET (exibir formulário) e POST (processar envio).
    if request.method == "POST":
        # Instancia o formulário com os dados enviados pelo navegador.
        form = AlunoForm(request.POST)

        # .is_valid() valida todos os campos segundo as regras do Model e do Form.
        if form.is_valid():
            # commit=False → prepara o objeto Aluno mas NÃO salva no banco ainda.
            # Precisamos adicionar o 'user' antes de salvar.
            aluno = form.save(commit=False)

            # Verificação manual de duplicidade de matrícula no User do Django.
            if User.objects.filter(username=aluno.matricula).exists():
                messages.error(request, "Já existe um usuário com essa matrícula.")
                return render(request, "alunos/form.html", {
                    "form": form,
                    "aluno": None,
                })

            # get_or_create → busca o grupo; se não existir, cria automaticamente.
            # Retorna uma tupla (objeto, criado_agora); o "_" descarta o booleano.
            grupo_aluno, _ = Group.objects.get_or_create(name="Aluno")

            # create_user é o método correto para criar usuários pois faz o hash da senha.
            # Nunca usar User.objects.create() diretamente, pois salvaria a senha em texto puro.
            user = User.objects.create_user(
                username=aluno.matricula,
                email=aluno.email,
                password="aluno123",
                first_name=aluno.nome,
            )

            # Adiciona o usuário ao grupo "Aluno" para controle de permissões.
            user.groups.add(grupo_aluno)

            # Cria o perfil de usuário com tipo ALUNO e marca senha como temporária.
            PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    "tipo": PerfilUsuario.Tipo.ALUNO,
                    "senha_temporaria": True,
                }
            )

            # Agora que o User existe, vinculamos ao Aluno e salvamos no banco.
            aluno.user = user
            aluno.save()

            # Adiciona uma mensagem de sucesso que será exibida na próxima página.
            messages.success(
                request,
                "Aluno cadastrado com sucesso. Senha inicial: aluno123"
            )

            # Redireciona para a lista de alunos usando o name da URL.
            return redirect("alunos_list")
    else:
        # Requisição GET: exibe o formulário vazio.
        form = AlunoForm()

    return render(request, "alunos/form.html", {
        "form": form,
        "aluno": None,  # None indica ao template que é um cadastro novo (não edição).
    })


# =============================================================================
# VIEW: EDITAR ALUNO
# =============================================================================

@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def editar_aluno(request, pk):
    # 'pk' vem da URL: /alunos/3/editar/ → pk=3
    # get_object_or_404 retorna o Aluno com esse ID ou página 404 se não existir.
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        # instance=aluno → pré-preenche o formulário com os dados existentes
        # e garante que o .save() atualize o registro em vez de criar um novo.
        form = AlunoForm(request.POST, instance=aluno)

        if form.is_valid():
            aluno_editado = form.save(commit=False)

            # Verifica se outra conta (não a do próprio aluno) já usa essa matrícula.
            # .exclude(pk=aluno.user.pk) → ignora o próprio usuário na busca.
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

            # Salva o Aluno no banco de dados.
            aluno_editado.save()

            # Mantém o User do Django sincronizado com os dados do Aluno.
            aluno.user.username = aluno_editado.matricula
            aluno.user.email = aluno_editado.email
            aluno.user.first_name = aluno_editado.nome
            aluno.user.is_active = aluno_editado.ativo  # Desativa login se inativo.
            aluno.user.save()

            messages.success(request, "Aluno atualizado com sucesso.")
            return redirect("alunos_list")
    else:
        # GET: carrega o formulário já preenchido com os dados do aluno.
        form = AlunoForm(instance=aluno)

    return render(request, "alunos/form.html", {
        "form": form,
        "aluno": aluno,  # Passamos o aluno para o template saber que é uma edição.
    })


# =============================================================================
# VIEW: EXCLUIR (INATIVAR) ALUNO
# =============================================================================

@login_required
@user_passes_test(usuario_secretaria)
@transaction.atomic
def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        # "Soft delete": não apagamos o registro do banco.
        # Apenas marcamos o aluno como inativo para preservar o histórico.
        aluno.ativo = False
        # update_fields=["ativo"] → UPDATE parcial: atualiza somente essa coluna.
        aluno.save(update_fields=["ativo"])

        # Desativa também o login do usuário correspondente.
        aluno.user.is_active = False
        aluno.user.save(update_fields=["is_active"])

        messages.success(request, "Aluno inativado com sucesso.")
        return redirect("alunos_list")

    # GET: exibe página de confirmação antes de inativar.
    return render(request, "alunos/confirm_delete.html", {
        "aluno": aluno,
    })