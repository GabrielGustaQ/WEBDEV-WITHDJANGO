from django import forms

from apps.alunos.models import Aluno
from apps.disciplinas.models import Disciplina


class MatriculaForm(forms.Form):
    aluno = forms.ModelChoiceField(
        label="Aluno",
        queryset=Aluno.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    disciplina = forms.ModelChoiceField(
        label="Disciplina",
        queryset=Disciplina.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["aluno"].queryset = Aluno.objects.filter(
            ativo=True
        ).order_by("nome")

        self.fields["disciplina"].queryset = Disciplina.objects.filter(
            ativa=True,
            vagas_disponiveis__gt=0,
        ).order_by("nome")