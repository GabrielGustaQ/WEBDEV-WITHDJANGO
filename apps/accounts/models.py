from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):
    class Tipo(models.TextChoices):
        SECRETARIA = "secretaria", "Secretaria"
        ALUNO = "aluno", "Aluno"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.ALUNO
    )

    senha_temporaria = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de usuário"
        verbose_name_plural = "Perfis de usuários"

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_display()}"

    @property
    def is_secretaria(self):
        return self.tipo == self.Tipo.SECRETARIA

    @property
    def is_aluno(self):
        return self.tipo == self.Tipo.ALUNO