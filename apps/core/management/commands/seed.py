from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from apps.alunos.models import Aluno
from apps.disciplinas.models import Disciplina
from apps.matriculas.services import realizar_matricula


class Command(BaseCommand):
    help = "Popula o banco com dados iniciais para testes."

    def handle(self, *args, **kwargs):
        secretaria_group, _ = Group.objects.get_or_create(name="Secretaria")
        aluno_group, _ = Group.objects.get_or_create(name="Aluno")

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@email.com",
                "is_staff": True,
                "is_superuser": True,
            }
        )

        if created:
            admin.set_password("admin123")
            admin.save()

        admin.groups.add(secretaria_group)

        alunos_data = [
            {
                "username": "2024001",
                "password": "aluno123",
                "nome": "Maria Silva",
                "matricula": "2024001",
                "email": "maria@email.com",
                "curso": "Ciência da Computação",
                "telefone": "77999990001",
            },
            {
                "username": "2024002",
                "password": "aluno123",
                "nome": "João Santos",
                "matricula": "2024002",
                "email": "joao@email.com",
                "curso": "Sistemas de Informação",
                "telefone": "77999990002",
            },
        ]

        alunos = []

        for data in alunos_data:
            user, user_created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "is_staff": False,
                    "is_superuser": False,
                }
            )

            if user_created:
                user.set_password(data["password"])
                user.save()

            user.groups.add(aluno_group)

            aluno, _ = Aluno.objects.get_or_create(
                matricula=data["matricula"],
                defaults={
                    "user": user,
                    "nome": data["nome"],
                    "email": data["email"],
                    "curso": data["curso"],
                    "telefone": data["telefone"],
                    "ativo": True,
                }
            )

            alunos.append(aluno)

        disciplinas_data = [
            {
                "nome": "Desenvolvimento Web",
                "codigo": "COMP001",
                "carga_horaria": 60,
                "periodo_letivo": "2026.1",
                "vagas_total": 30,
                "vagas_disponiveis": 30,
                "ativa": True,
            },
            {
                "nome": "Banco de Dados",
                "codigo": "COMP002",
                "carga_horaria": 60,
                "periodo_letivo": "2026.1",
                "vagas_total": 25,
                "vagas_disponiveis": 25,
                "ativa": True,
            },
            {
                "nome": "Engenharia de Software",
                "codigo": "COMP003",
                "carga_horaria": 60,
                "periodo_letivo": "2026.1",
                "vagas_total": 20,
                "vagas_disponiveis": 20,
                "ativa": True,
            },
        ]

        disciplinas = []

        for data in disciplinas_data:
            disciplina, _ = Disciplina.objects.get_or_create(
                codigo=data["codigo"],
                defaults=data
            )
            disciplinas.append(disciplina)

        try:
            realizar_matricula(alunos[0], disciplinas[0])
        except ValueError:
            pass

        try:
            realizar_matricula(alunos[1], disciplinas[1])
        except ValueError:
            pass

        self.stdout.write(self.style.SUCCESS("Seed executado com sucesso."))

        self.stdout.write("Usuário secretaria:")
        self.stdout.write("login: admin")
        self.stdout.write("senha: admin123")

        self.stdout.write("Usuário aluno:")
        self.stdout.write("login: 2024001")
        self.stdout.write("senha: aluno123")