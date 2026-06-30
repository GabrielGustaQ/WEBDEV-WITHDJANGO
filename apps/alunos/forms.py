# =============================================================================
# FORMS.PY — Formulários do Django
#
# O Django possui um sistema de formulários que cuida de:
#   1. Renderizar os campos HTML automaticamente
#   2. Validar os dados enviados pelo usuário
#   3. Converter os dados para os tipos corretos (string → inteiro, etc.)
#
# ModelForm é um atalho poderoso: ele gera o formulário direto do Model,
# evitando duplicação de código.
# =============================================================================

from django import forms
from .models import Aluno


# ModelForm lê o Model e cria campos de formulário automaticamente
# para cada campo do banco de dados listado em 'fields'.
class AlunoForm(forms.ModelForm):

    class Meta:
        # Diz ao formulário de qual Model ele deve gerar os campos.
        model = Aluno

        # Define quais colunas do Model viram campos no formulário.
        # Campos como 'criado_em' e 'atualizado_em' são omitidos pois
        # são preenchidos automaticamente pelo Django.
        fields = [
            "nome",
            "matricula",
            "email",
            "curso",
            "telefone",
            "ativo",
        ]

        # Widgets controlam COMO cada campo é renderizado no HTML.
        # Aqui adicionamos classes CSS do Bootstrap e textos de placeholder.
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome completo do aluno"
            }),
            "matricula": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 2024001"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "email@exemplo.com"
            }),
            "curso": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Curso do aluno"
            }),
            "telefone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Telefone"
            }),
            # CheckboxInput renderiza o campo booleano como uma caixa de seleção.
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

        # Labels são os rótulos exibidos acima de cada campo no formulário.
        # Sem isso, o Django usaria o nome do atributo Python (ex: "matricula").
        labels = {
            "nome": "Nome",
            "matricula": "Matrícula",
            "email": "E-mail",
            "curso": "Curso",
            "telefone": "Telefone",
            "ativo": "Aluno ativo",
        }