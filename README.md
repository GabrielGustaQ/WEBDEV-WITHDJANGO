# WEBDEV-WITHDJANGO

This project was developed as part of a Web Development course, focusing on building a web platform for managing academic pre-enrollments.

The application allows the academic office to manage students, courses/subjects, pre-enrollments and reports. It was built with Django and PostgreSQL, using Docker to simplify execution across different machines.

---

## How to run the project

The project runs entirely with Docker, so it is not necessary to manually install Python, PostgreSQL or Django on the host machine.

First, install Docker:

- Docker installation guide: https://docs.docker.com/get-docker/

After installing Docker, clone the repository and enter the project folder:

```bash
git clone <repository-url>
cd WEBDEV-WITHDJANGO
```

Create a `.env` file in the project root. You can use the example below:

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

Then run:

```bash
docker compose up --build
```

The application will automatically:

- start the PostgreSQL database;
- wait until the database is ready;
- generate Django migrations;
- apply migrations;
- run the seed command, if `SEED_DB=True`;
- start the Django development server.

Access the application at:

```
http://localhost:8001
```

> If the port mapping is changed in `docker-compose.yml`, use the configured host port.

To stop the containers:

```bash
docker compose down
```

---

## Default access

If the seed command is enabled, the project will create initial test data such as administrator users, students, subjects and enrollments.

Example credentials may be defined in:

```
apps/core/management/commands/seed.py
```

Check this file to see the current test users and passwords.

---

## Project structure

The project follows a simple Django architecture based on apps.

```
WEBDEV-WITHDJANGO/
├── apps/
│   ├── accounts/
│   ├── alunos/
│   ├── core/
│   ├── disciplinas/
│   ├── matriculas/
│   └── relatorios/
├── config/
├── static/
├── templates/
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── manage.py
└── requirements.txt
```

---

## Main modules

### `config/`

Contains the main Django project configuration.

| File | Description |
|---|---|
| `settings.py` | Django settings: installed apps, database, static files and templates |
| `urls.py` | Main URL routing for the project |
| `asgi.py` / `wsgi.py` | Django application entry points |

---

### `apps/accounts/`

Responsible for authentication and user access control.

- Login and logout
- Dashboard access
- User profile control
- Temporary password handling

---

### `apps/alunos/`

Responsible for student management.

- Register, list and update students
- Logical deletion / inactivation
- Link students to Django users

| File | Description |
|---|---|
| `models.py` | Defines the `Aluno` model |
| `forms.py` | Defines student forms |
| `views.py` | Request handling logic |
| `urls.py` | Student routes |

---

### `apps/disciplinas/`

Responsible for subject/course management.

- Register, list and update subjects
- Control total and available vacancies
- Logical deletion / inactivation when needed

| File | Description |
|---|---|
| `models.py` | Defines the `Disciplina` model |
| `forms.py` | Defines subject forms |
| `views.py` | Subject CRUD logic |
| `urls.py` | Subject routes |

---

### `apps/matriculas/`

Responsible for pre-enrollment operations.

- Create pre-enrollments
- Prevent duplicated active enrollments for the same subject and term
- Check available vacancies before confirming
- Decrement vacancies on confirmation; restore on cancellation
- Cancel enrollments

| File | Description |
|---|---|
| `models.py` | Defines the `Matricula` model |
| `forms.py` | Defines enrollment forms |
| `services.py` | Centralizes business rules for enrollment and cancellation |
| `views.py` | Enrollment pages and actions |
| `urls.py` | Enrollment routes |

---

### `apps/relatorios/`

Responsible for academic reports.

- Enrollments by subject
- Subjects with available vacancies
- Student enrollment history

| File | Description |
|---|---|
| `views.py` | Report queries and rendering logic |
| `urls.py` | Report routes |

---

### `apps/core/`

Contains general project support code, including the seed command for creating initial test data.

```bash
# Run the seed manually
docker compose run --rm web python manage.py seed
```

---

## Templates and static files

The frontend uses Django Templates with HTML, CSS and Bootstrap.

```
templates/
├── base.html
├── login.html
└── dashboard.html

static/
├── css/
│   └── style.css
└── js/
    └── app.js
```

---

## Docker files

### `Dockerfile`

Defines the Python environment, installs system dependencies, installs Python packages and copies the project files into the container.

### `docker-compose.yml`

Defines two services:

| Service | Description |
|---|---|
| `db` | PostgreSQL 16 database |
| `web` | Django application |

### `entrypoint.sh`

Runs the startup routine for the Django container:

1. Waits for PostgreSQL to be ready
2. Generates migrations (`makemigrations`)
3. Applies migrations (`migrate`)
4. Runs seed if `SEED_DB=True`
5. Starts the Django development server

---

## Useful commands

```bash
# Run the project
docker compose up --build

# Run in detached mode
docker compose up -d --build

# Stop containers
docker compose down

# View logs
docker compose logs -f web

# Create migrations manually
docker compose run --rm web python manage.py makemigrations

# Apply migrations manually
docker compose run --rm web python manage.py migrate

# Run seed manually
docker compose run --rm web python manage.py seed

# Create a Django superuser
docker compose run --rm web python manage.py createsuperuser
```

---

## Academic objective

The system was designed to support the pre-enrollment process in an academic institution. It helps administrators manage students, subjects and pre-enrollments, while also providing reports that support decision-making about course demand and available vacancies.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · Django |
| Database | PostgreSQL 16 |
| Frontend | HTML · CSS · Bootstrap · JavaScript |
| Infrastructure | Docker · Docker Compose |

---

## Authors

- Fláira Hanny Bomfim dos Santos
- Gabriel Gustavo Santos Queiroz
- Gabriel Lopes Aguiar
- Iago Fabricio Meira Pereira

> Universidade Estadual do Sudoeste da Bahia — Bacharelado em Ciência da Computação · 2026