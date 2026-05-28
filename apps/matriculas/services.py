from django.db import transaction
from django.utils import timezone

from apps.disciplinas.models import Disciplina
from apps.matriculas.models import Matricula


@transaction.atomic
def realizar_matricula(aluno, disciplina):
    disciplina = Disciplina.objects.select_for_update().get(id=disciplina.id)

    if not aluno.ativo:
        raise ValueError("Aluno inativo não pode realizar matrícula.")

    if not disciplina.ativa:
        raise ValueError("Disciplina inativa não pode receber matrícula.")

    if disciplina.vagas_disponiveis <= 0:
        raise ValueError("Não há vagas disponíveis para esta disciplina.")

    ja_matriculado = Matricula.objects.filter(
        aluno=aluno,
        disciplina=disciplina,
        periodo_letivo=disciplina.periodo_letivo,
    ).exclude(
        status=Matricula.STATUS_CANCELADA
    ).exists()

    if ja_matriculado:
        raise ValueError("Aluno já possui matrícula ativa nesta disciplina e período.")

    matricula = Matricula.objects.create(
        aluno=aluno,
        disciplina=disciplina,
        periodo_letivo=disciplina.periodo_letivo,
        status=Matricula.STATUS_CONFIRMADA,
    )

    disciplina.vagas_disponiveis -= 1
    disciplina.save(update_fields=["vagas_disponiveis"])

    return matricula


@transaction.atomic
def cancelar_matricula(matricula):
    if matricula.status == Matricula.STATUS_CANCELADA:
        raise ValueError("Esta matrícula já está cancelada.")

    disciplina = Disciplina.objects.select_for_update().get(
        id=matricula.disciplina.id
    )

    matricula.status = Matricula.STATUS_CANCELADA
    matricula.cancelada_em = timezone.now()
    matricula.save(update_fields=["status", "cancelada_em"])

    if disciplina.ativa:
        disciplina.vagas_disponiveis += 1
        disciplina.save(update_fields=["vagas_disponiveis"])

    return matricula