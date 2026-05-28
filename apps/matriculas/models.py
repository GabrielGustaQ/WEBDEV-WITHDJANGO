from django.db import models
from django.db.models import Q

from apps.alunos.models import Aluno
from apps.disciplinas.models import Disciplina


class Matricula(models.Model):
    STATUS_CONFIRMADA = "confirmada"
    STATUS_PENDENTE = "pendente"
    STATUS_CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (STATUS_CONFIRMADA, "Confirmada"),
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        related_name="matriculas"
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="matriculas"
    )
    periodo_letivo = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CONFIRMADA
    )

    criada_em = models.DateTimeField(auto_now_add=True)
    cancelada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criada_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "disciplina", "periodo_letivo"],
                condition=~Q(status="cancelada"),
                name="uniq_matricula_ativa_por_periodo"
            )
        ]

    def __str__(self):
        return f"{self.aluno} - {self.disciplina} - {self.status}"