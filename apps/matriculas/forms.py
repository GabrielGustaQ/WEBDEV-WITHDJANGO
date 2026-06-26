from django import forms

from apps.alunos.models import Aluno
from apps.disciplinas.models import Turma


class MatriculaForm(forms.Form):
    aluno = forms.ModelChoiceField(
        label="Aluno",
        queryset=Aluno.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    turma = forms.ModelChoiceField(
        label="Turma",
        queryset=Turma.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["aluno"].queryset = Aluno.objects.filter(
            ativo=True
        ).order_by("nome")

        self.fields["turma"].queryset = Turma.objects.filter(
            ativa=True,
            vagas_disponiveis__gt=0,
        ).select_related("disciplina").order_by("disciplina__nome", "periodo_letivo")
