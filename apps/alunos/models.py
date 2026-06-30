# =============================================================================
# MODELS.PY — A "Camada de Dados" do Django (M do padrão MTV)
#
# O Model é a representação de uma tabela do banco de dados em Python.
# Cada atributo da classe vira uma coluna na tabela.
# O Django cuida de criar e gerenciar essa tabela via "migrations".
# =============================================================================

# 'models' contém os tipos de campo (CharField, EmailField, etc.)
from django.db import models

# O Django já possui um sistema de usuários embutido — importamos aqui para
# criar um vínculo entre nosso Aluno e o usuário de login.
from django.contrib.auth.models import User


# Todo Model herda de models.Model — isso dá acesso ao ORM do Django,
# que permite fazer consultas ao banco sem escrever SQL diretamente.
class Aluno(models.Model):

    # OneToOneField cria uma relação 1-para-1 com o User do Django.
    # Isso vincula o perfil de aluno a uma conta de login.
    # on_delete=PROTECT impede que o User seja deletado enquanto existir um Aluno ligado a ele.
    # related_name="aluno" permite acessar o aluno a partir do user: user.aluno
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="aluno"
    )

    # CharField → coluna VARCHAR no banco. max_length define o limite de caracteres.
    nome = models.CharField(max_length=150)

    # unique=True cria uma restrição no banco: não pode haver dois alunos com a mesma matrícula.
    matricula = models.CharField(max_length=30, unique=True)

    # EmailField é um CharField com validação de formato de e-mail.
    email = models.EmailField(unique=True)

    curso = models.CharField(max_length=100)

    # blank=True significa que o campo é opcional no formulário (não obrigatório).
    telefone = models.CharField(max_length=20, blank=True)

    # BooleanField → coluna booleana (verdadeiro/falso). Usado para "soft delete":
    # em vez de apagar o registro, apenas o marcamos como inativo.
    ativo = models.BooleanField(default=True)

    # auto_now_add=True → preenchido automaticamente na criação do registro.
    criado_em = models.DateTimeField(auto_now_add=True)

    # auto_now=True → atualizado automaticamente a cada vez que o registro é salvo.
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        # Define a ordenação padrão das consultas: sempre virão por nome alfabético.
        ordering = ["nome"]

    def __str__(self):
        # Representação legível do objeto — aparece no Admin e em logs.
        return f"{self.nome} - {self.matricula}"