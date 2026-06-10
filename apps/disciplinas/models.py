from django.core.exceptions import ValidationError
from django.db import models


class Disciplina(models.Model):
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30, unique=True)
    carga_horaria = models.PositiveIntegerField()
    periodo_letivo = models.CharField(max_length=20)

    vagas_total = models.PositiveIntegerField()
    vagas_disponiveis = models.PositiveIntegerField()

    ativa = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    @property
    def vagas_ocupadas(self):
        return self.vagas_total - self.vagas_disponiveis

    def clean(self):
        if self.vagas_disponiveis > self.vagas_total:
            raise ValidationError(
                "As vagas disponíveis não podem ser maiores que o total de vagas."
            )