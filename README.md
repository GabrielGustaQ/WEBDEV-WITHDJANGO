# WEBDEV-WITHDJANGO

Academic pre-enrollment management system built with Django and PostgreSQL.

The application supports two roles: **secretaria** (admin) manages students, subjects, classes and enrollments; **alunos** (students) enroll themselves, track their own history and check available vacancies.

---

## How to run

The project runs entirely with Docker — no local Python, PostgreSQL or Django installation required.

Install Docker: https://docs.docker.com/get-docker/

Clone the repository and enter the project folder:

```bash
git clone <repository-url>
cd WEBDEV-WITHDJANGO
```

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=dev-secret-key

DATABASE_NAME=prematricula
DATABASE_USER=prematricula_user
DATABASE_PASSWORD=prematricula_password
DATABASE_HOST=db
DATABASE_PORT=5432

SEED_DB=True
```

Start the project:

```bash
docker compose up --build
```

On startup the container will automatically:

1. Wait for PostgreSQL to be ready
2. Generate migrations (`makemigrations`)
3. Apply migrations (`migrate`)
4. Run the seed command if `SEED_DB=True`
5. Start the Django development server

Access the application at `http://localhost:8001`.

To stop:

```bash
docker compose down
```

---

## Default access

When `SEED_DB=True`, initial test data is created including admin users, students, subjects and enrollments.

Check `apps/core/management/commands/seed.py` for the current test credentials.

---

## Database schema

The following tables represent the core application models. Django's built-in `auth_user` table is used for authentication and linked to both `PerfilUsuario` and `Aluno`.

```
┌─────────────────────────────────────────────┐
│                  auth_user                  │
├──────────────────┬──────────────────────────┤
│ id               │ BIGINT (PK)              │
│ username         │ VARCHAR(150)             │
│ email            │ VARCHAR(254)             │
│ password         │ VARCHAR(128)             │
│ first_name       │ VARCHAR(150)             │
│ last_name        │ VARCHAR(150)             │
│ is_staff         │ BOOLEAN                  │
│ is_superuser     │ BOOLEAN                  │
└──────────────────┴──────────────────────────┘
        │                        │
        │ OneToOne               │ OneToOne
        ▼                        ▼
┌───────────────────────┐   ┌───────────────────────────┐
│  accounts_perfilusuario│   │       alunos_aluno        │
├────────────┬──────────┤   ├──────────────┬────────────┤
│ id         │ BIGINT PK│   │ id           │ BIGINT PK  │
│ user_id    │ FK       │   │ user_id      │ FK (UNIQUE)│
│ tipo       │ VARCHAR  │   │ nome         │ VARCHAR    │
│            │ secretaria│   │ matricula    │ VARCHAR    │
│            │ aluno    │   │              │ (UNIQUE)   │
│ senha_temp │ BOOLEAN  │   │ email        │ VARCHAR    │
│ criado_em  │ TIMESTAMP│   │              │ (UNIQUE)   │
│ atualizado │ TIMESTAMP│   │ curso        │ VARCHAR    │
└────────────┴──────────┘   │ telefone     │ VARCHAR    │
                             │ ativo        │ BOOLEAN    │
                             │ criado_em    │ TIMESTAMP  │
                             │ atualizado_em│ TIMESTAMP  │
                             └──────────────┴────────────┘
                                        │
                                        │ FK (aluno_id)
                                        ▼
┌──────────────────────────────────────────────┐
│              matriculas_matricula             │
├───────────────────┬──────────────────────────┤
│ id                │ BIGINT (PK)              │
│ aluno_id          │ FK → alunos_aluno        │
│ turma_id          │ FK → disciplinas_turma   │
│ status            │ VARCHAR                  │
│                   │ confirmada               │
│                   │ pendente                 │
│                   │ cancelada                │
│ criada_em         │ TIMESTAMP                │
│ cancelada_em      │ TIMESTAMP (nullable)     │
└───────────────────┴──────────────────────────┘
         ▲
         │ FK (turma_id)
         │
┌──────────────────────────────────────────────┐
│             disciplinas_turma                │
├───────────────────┬──────────────────────────┤
│ id                │ BIGINT (PK)              │
│ disciplina_id     │ FK → disciplinas_disciplina│
│ periodo_letivo    │ VARCHAR(20)              │
│ vagas_total       │ POSITIVE INT             │
│ vagas_disponiveis │ POSITIVE INT             │
│ ativa             │ BOOLEAN                  │
│ criado_em         │ TIMESTAMP                │
│ atualizado_em     │ TIMESTAMP                │
└───────────────────┴──────────────────────────┘
         ▲
         │ FK (disciplina_id)
         │
┌──────────────────────────────────────────────┐
│          disciplinas_disciplina              │
├───────────────────┬──────────────────────────┤
│ id                │ BIGINT (PK)              │
│ nome              │ VARCHAR(120)             │
│ codigo            │ VARCHAR(30) (UNIQUE)     │
│ ementa            │ TEXT                     │
│ carga_horaria     │ POSITIVE INT (nullable)  │
│ criado_em         │ TIMESTAMP                │
│ atualizado_em     │ TIMESTAMP                │
└───────────────────┴──────────────────────────┘
```

### Relationships summary

```
auth_user ──── 1:1 ────► PerfilUsuario   (role: secretaria | aluno)
auth_user ──── 1:1 ────► Aluno           (only for student users)
Aluno     ──── 1:N ────► Matricula
Turma     ──── 1:N ────► Matricula
Disciplina──── 1:N ────► Turma
```

### Key constraints

```
UNIQUE (aluno_id, turma_id)  WHERE status != 'cancelada'
  → prevents duplicate active enrollment in the same class

UNIQUE (disciplina_id, periodo_letivo)
  → one class per subject per term
```

---

## Project structure

```
WEBDEV-WITHDJANGO/
├── apps/
│   ├── accounts/       # auth, login, user profiles and roles
│   ├── alunos/         # student CRUD
│   ├── core/           # seed command and shared utilities
│   ├── disciplinas/    # subjects (Disciplina) and classes (Turma)
│   ├── matriculas/     # enrollments: admin management + student self-enrollment
│   └── relatorios/     # reports: by subject, vacancies, student history
├── config/             # Django settings and main URL conf
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── accounts/
│   ├── alunos/
│   ├── disciplinas/
│   ├── matriculas/
│   ├── relatorios/
│   └── turmas/
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── manage.py
└── requirements.txt
```

---

## Role-based access

### Secretaria (admin)

| Feature | Path |
|---|---|
| Dashboard | `/` |
| Students | `/alunos/` |
| Subjects | `/disciplinas/` |
| Classes | `/turmas/` |
| Enrollments | `/matriculas/` |
| Report — by subject | `/relatorios/matriculas-por-disciplina/` |
| Report — vacancies | `/relatorios/disciplinas-com-vagas/` |
| Report — student history | `/relatorios/historico-aluno/` |

### Aluno (student)

| Feature | Path |
|---|---|
| Dashboard | `/` |
| Self-enroll | `/matriculas/matricular/` |
| My enrollments | `/matriculas/minhas/` |
| Available vacancies | `/relatorios/vagas/` |
| My history | `/relatorios/meu-historico/` |

> The vacancy report is sorted **fewest vacancies first** for admins and **most vacancies first** for students. The student self-enrollment page only shows classes where the student is not yet enrolled.

---

## Modules

### `apps/accounts/`

Authentication and role management.

- Login / logout with redirect by role
- `PerfilUsuario` model: links `auth_user` to a role (`secretaria` or `aluno`)
- Temporary password flow (forces password change on first login)
- `usuario_secretaria()` helper used as `user_passes_test` guard on admin views

### `apps/alunos/`

Student management (admin only).

- Full CRUD: register, list, update, deactivate
- One-to-one link between `Aluno` and `auth_user`

### `apps/disciplinas/`

Subjects and classes management.

- `Disciplina`: name, code, syllabus, workload
- `Turma`: links a subject to a term with total and available vacancies
- Unique constraint: one class per subject per term

### `apps/matriculas/`

Enrollment operations.

- Admin can create and cancel enrollments for any student
- Student can self-enroll through `/matriculas/matricular/`
- `services.py` centralizes business logic with `select_for_update` to prevent race conditions:
  - validates student and class are active
  - checks available vacancies
  - prevents duplicate active enrollment
  - decrements `vagas_disponiveis` on enroll; restores on cancellation

### `apps/relatorios/`

Read-only reports.

| View | Role | Description |
|---|---|---|
| `matriculas_por_disciplina` | admin | all enrollments, filterable by subject and term |
| `disciplinas_com_vagas` | admin | active classes sorted fewest → most vacancies |
| `historico_aluno` | admin | search any student's enrollment history |
| `disciplinas_com_vagas_aluno` | student | active classes with vacancies sorted most → fewest |
| `meu_historico` | student | logged-in student's own enrollment history |

### `apps/core/`

Support code and the database seed command.

```bash
docker compose run --rm web python manage.py seed
```

---

## Docker

### `Dockerfile`

Builds the Python environment, installs system and Python dependencies, copies the project.

### `docker-compose.yml`

| Service | Description |
|---|---|
| `db` | PostgreSQL 16 |
| `web` | Django application |

### `entrypoint.sh`

1. Waits for PostgreSQL
2. `makemigrations`
3. `migrate`
4. `seed` (if `SEED_DB=True`)
5. Starts the dev server

---

## Useful commands

```bash
# Start the project
docker compose up --build

# Start in detached mode
docker compose up -d --build

# Stop containers
docker compose down

# View logs
docker compose logs -f web

# Generate migrations
docker compose run --rm web python manage.py makemigrations

# Apply migrations
docker compose run --rm web python manage.py migrate

# Run seed
docker compose run --rm web python manage.py seed

# Create a superuser
docker compose run --rm web python manage.py createsuperuser
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · Django 5 |
| Database | PostgreSQL 16 |
| Frontend | HTML · CSS · Bootstrap 5 · Bootstrap Icons |
| Infrastructure | Docker · Docker Compose |

---

## Authors

- Fláira Hanny Bomfim dos Santos
- Gabriel Gustavo Santos Queiroz
- Gabriel Lopes Aguiar
- Iago Fabricio Meira Pereira

> Universidade Estadual do Sudoeste da Bahia — Bacharelado em Ciência da Computação · 2026
