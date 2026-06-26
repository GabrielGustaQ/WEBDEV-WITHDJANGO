from django import forms

from .models import Disciplina, Turma


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["nome", "codigo", "carga_horaria", "ementa"]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome da disciplina",
            }),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: COMP001",
            }),
            "carga_horaria": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "ementa": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descrição da ementa (opcional)",
            }),
        }

        labels = {
            "nome": "Nome",
            "codigo": "Código",
            "carga_horaria": "Carga horária (h)",
            "ementa": "Ementa",
        }


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = [
            "disciplina",
            "periodo_letivo",
            "vagas_total",
            "vagas_disponiveis",
            "ativa",
        ]

        widgets = {
            "disciplina": forms.Select(attrs={
                "class": "form-select",
            }),
            "periodo_letivo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 2026.1",
            }),
            "vagas_total": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "vagas_disponiveis": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "ativa": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "disciplina": "Disciplina",
            "periodo_letivo": "Período letivo",
            "vagas_total": "Total de vagas",
            "vagas_disponiveis": "Vagas disponíveis",
            "ativa": "Turma ativa",
        }

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
