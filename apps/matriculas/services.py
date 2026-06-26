from django.db import transaction
from django.utils import timezone

from apps.disciplinas.models import Turma

from .models import Matricula


@transaction.atomic
def realizar_matricula(aluno, turma):
    turma = Turma.objects.select_for_update().get(pk=turma.pk)

    if not aluno.ativo:
        raise ValueError("Aluno inativo não pode realizar matrícula.")

    if not turma.ativa:
        raise ValueError("Turma inativa não pode receber matrícula.")

    if turma.vagas_disponiveis <= 0:
        raise ValueError("Não há vagas disponíveis para esta turma.")

    ja_matriculado = Matricula.objects.filter(
        aluno=aluno,
        turma=turma,
    ).exclude(
        status=Matricula.STATUS_CANCELADA
    ).exists()

    if ja_matriculado:
        raise ValueError("Aluno já possui matrícula ativa nesta turma.")

    matricula = Matricula.objects.create(
        aluno=aluno,
        turma=turma,
        status=Matricula.STATUS_CONFIRMADA,
    )

    turma.vagas_disponiveis -= 1
    turma.save(update_fields=["vagas_disponiveis"])

    return matricula


@transaction.atomic
def cancelar_matricula(matricula):
    if matricula.status == Matricula.STATUS_CANCELADA:
        raise ValueError("Esta matrícula já está cancelada.")

    turma = Turma.objects.select_for_update().get(pk=matricula.turma.pk)

    matricula.status = Matricula.STATUS_CANCELADA
    matricula.cancelada_em = timezone.now()
    matricula.save(update_fields=["status", "cancelada_em"])

    if turma.ativa:
        turma.vagas_disponiveis += 1
        turma.save(update_fields=["vagas_disponiveis"])

    return matricula
