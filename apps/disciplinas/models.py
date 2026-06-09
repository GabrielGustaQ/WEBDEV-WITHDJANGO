from django.db import models

class Disciplina(models.Model):
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30, unique=True)
    carga_horaria = models.PositiveIntegerField()

    vagas_total = models.PositiveIntegerField()
    vagas_ocupadas = models.PositiveIntegerField(default=0) 
   
    ativa = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "disciplina"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    @property
    def vagas_disponiveis(self):
        return self.vagas_total - self.vagas_ocupadas

class HorarioDisciplina(models.Model):
    DIA_CHOICES = [
        ('segunda', 'Segunda'),
        ('terca', 'Terça'),
        ('quarta', 'Quarta'),
        ('quinta', 'Quinta'),
        ('sexta', 'Sexta'),
        ('sabado', 'Sábado'),
    ]

    disciplina = models.ForeignKey(
        Disciplina, 
        on_delete=models.CASCADE, 
        related_name="horarios"
    )
    dia_semana = models.CharField(max_length=15, choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        db_table = "horario_disciplina"

    def __str__(self):
        return f"{self.disciplina.codigo} | {self.dia_semana} ({self.hora_inicio} - {self.hora_fim})"