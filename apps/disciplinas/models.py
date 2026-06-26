from django.core.exceptions import ValidationError
from django.db import models


class Disciplina(models.Model):
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30, unique=True)
    ementa = models.TextField(blank=True)
    carga_horaria = models.PositiveIntegerField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Turma(models.Model):
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="turmas",
    )

    periodo_letivo = models.CharField(max_length=20)
    vagas_total = models.PositiveIntegerField()
    vagas_disponiveis = models.PositiveIntegerField()
    ativa = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["disciplina__nome", "periodo_letivo"]
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        constraints = [
            models.UniqueConstraint(
                fields=["disciplina", "periodo_letivo"],
                name="uniq_turma_disciplina_periodo",
            )
        ]

    def __str__(self):
        return f"{self.disciplina.codigo} - {self.disciplina.nome} ({self.periodo_letivo})"

    @property
    def vagas_ocupadas(self):
        return self.vagas_total - self.vagas_disponiveis

    def clean(self):
        if self.vagas_disponiveis > self.vagas_total:
            raise ValidationError(
                "As vagas disponíveis não podem ser maiores que o total de vagas."
            )
