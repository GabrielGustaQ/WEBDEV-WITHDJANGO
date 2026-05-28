from django import forms
from .models import Disciplina


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = [
            "nome",
            "codigo",
            "carga_horaria",
            "periodo_letivo",
            "vagas_total",
            "vagas_disponiveis",
            "ativa",
        ]

    def clean(self):
        cleaned_data = super().clean()
        vagas_total = cleaned_data.get("vagas_total")
        vagas_disponiveis = cleaned_data.get("vagas_disponiveis")

        if vagas_total is not None and vagas_disponiveis is not None:
            if vagas_disponiveis > vagas_total:
                raise forms.ValidationError(
                    "As vagas disponíveis não podem ser maiores que o total de vagas."
                )

        return cleaned_data