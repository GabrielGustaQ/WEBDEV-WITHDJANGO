from django import forms
from .models import Aluno


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = [
            "nome",
            "matricula",
            "email",
            "curso",
            "telefone",
            "ativo",
        ]

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
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

        labels = {
            "nome": "Nome",
            "matricula": "Matrícula",
            "email": "E-mail",
            "curso": "Curso",
            "telefone": "Telefone",
            "ativo": "Aluno ativo",
        }