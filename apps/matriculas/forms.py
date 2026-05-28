from django import forms

from apps.alunos.models import Aluno
from apps.disciplinas.models import Disciplina


class MatriculaForm(forms.Form):
    aluno = forms.ModelChoiceField(
        queryset=Aluno.objects.filter(ativo=True),
        label="Aluno"
    )

    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.filter(
            ativa=True,
            vagas_disponiveis__gt=0
        ),
        label="Disciplina"
    )