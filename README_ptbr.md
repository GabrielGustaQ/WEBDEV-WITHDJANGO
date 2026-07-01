# WEBDEV-WITHDJANGO

Sistema de pré-matrícula acadêmica construído com Django e PostgreSQL.

A aplicação suporta dois perfis: **secretaria** (admin) gerencia alunos, disciplinas, turmas e matrículas; **alunos** realizam a própria pré-matrícula, acompanham o histórico e consultam vagas disponíveis.

---

## Como executar

O projeto roda inteiramente com Docker — sem necessidade de instalar Python, PostgreSQL ou Django localmente.

Instale o Docker: https://docs.docker.com/get-docker/

Clone o repositório e entre na pasta do projeto:

```bash
git clone <url-do-repositório>
cd WEBDEV-WITHDJANGO
```

Crie um arquivo `.env` na raiz do projeto:

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

Inicie o projeto:

```bash
docker compose up --build
```

Na inicialização, o container irá automaticamente:

1. Aguardar o PostgreSQL ficar disponível
2. Gerar as migrations (`makemigrations`)
3. Aplicar as migrations (`migrate`)
4. Executar o comando seed se `SEED_DB=True`
5. Iniciar o servidor de desenvolvimento do Django

Acesse a aplicação em `http://localhost:8001`.

Para parar:

```bash
docker compose down
```

---

## Acesso padrão

Com `SEED_DB=True`, dados iniciais de teste são criados, incluindo usuários admin, alunos, disciplinas e matrículas.

Consulte `apps/core/management/commands/seed.py` para verificar as credenciais de teste atuais.

---

## Esquema do banco de dados

As tabelas abaixo representam os modelos principais da aplicação. A tabela `auth_user` nativa do Django é usada para autenticação e está vinculada tanto a `PerfilUsuario` quanto a `Aluno`.

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

### Resumo dos relacionamentos

```
auth_user ──── 1:1 ────► PerfilUsuario   (perfil: secretaria | aluno)
auth_user ──── 1:1 ────► Aluno           (apenas para usuários do tipo aluno)
Aluno     ──── 1:N ────► Matricula
Turma     ──── 1:N ────► Matricula
Disciplina──── 1:N ────► Turma
```

### Restrições principais

```
UNIQUE (aluno_id, turma_id)  WHERE status != 'cancelada'
  → impede matrícula ativa duplicada na mesma turma

UNIQUE (disciplina_id, periodo_letivo)
  → apenas uma turma por disciplina por período
```

---

## Estrutura do projeto

```
WEBDEV-WITHDJANGO/
├── apps/
│   ├── accounts/       # autenticação, login, perfis e papéis de usuário
│   ├── alunos/         # CRUD de alunos
│   ├── core/           # comando seed e utilitários compartilhados
│   ├── disciplinas/    # disciplinas (Disciplina) e turmas (Turma)
│   ├── matriculas/     # matrículas: gerenciamento admin + auto-matrícula do aluno
│   └── relatorios/     # relatórios: por disciplina, vagas, histórico do aluno
├── config/             # configurações do Django e URL conf principal
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

## Controle de acesso por perfil

### Secretaria (admin)

| Funcionalidade | Caminho |
|---|---|
| Dashboard | `/` |
| Alunos | `/alunos/` |
| Disciplinas | `/disciplinas/` |
| Turmas | `/turmas/` |
| Matrículas | `/matriculas/` |
| Relatório — por disciplina | `/relatorios/matriculas-por-disciplina/` |
| Relatório — vagas | `/relatorios/disciplinas-com-vagas/` |
| Relatório — histórico do aluno | `/relatorios/historico-aluno/` |

### Aluno

| Funcionalidade | Caminho |
|---|---|
| Dashboard | `/` |
| Auto-matrícula | `/matriculas/matricular/` |
| Minhas matrículas | `/matriculas/minhas/` |
| Vagas disponíveis | `/relatorios/vagas/` |
| Meu histórico | `/relatorios/meu-historico/` |

> O relatório de vagas é ordenado com **menos vagas primeiro** para admins e **mais vagas primeiro** para alunos. A página de auto-matrícula exibe apenas turmas em que o aluno ainda não está matriculado.

---

## Módulos

### `apps/accounts/`

Autenticação e gerenciamento de perfis.

- Login / logout com redirecionamento por perfil
- Modelo `PerfilUsuario`: vincula `auth_user` a um papel (`secretaria` ou `aluno`)
- Fluxo de senha temporária (força troca de senha no primeiro acesso)
- Helper `usuario_secretaria()` usado como guarda `user_passes_test` nas views admin

### `apps/alunos/`

Gerenciamento de alunos (somente admin).

- CRUD completo: cadastro, listagem, atualização, desativação
- Vínculo um-para-um entre `Aluno` e `auth_user`

### `apps/disciplinas/`

Gerenciamento de disciplinas e turmas.

- `Disciplina`: nome, código, ementa, carga horária
- `Turma`: vincula uma disciplina a um período letivo com vagas totais e disponíveis
- Restrição única: uma turma por disciplina por período

### `apps/matriculas/`

Operações de matrícula.

- Admin pode criar e cancelar matrículas para qualquer aluno
- Aluno pode se auto-matricular via `/matriculas/matricular/`
- `services.py` centraliza a lógica de negócio com `select_for_update` para evitar condições de corrida:
  - valida se aluno e turma estão ativos
  - verifica vagas disponíveis
  - impede matrícula ativa duplicada
  - decrementa `vagas_disponiveis` ao matricular; restaura ao cancelar

### `apps/relatorios/`

Relatórios somente leitura.

| View | Perfil | Descrição |
|---|---|---|
| `matriculas_por_disciplina` | admin | todas as matrículas, filtrável por disciplina e período |
| `disciplinas_com_vagas` | admin | turmas ativas ordenadas de menos para mais vagas |
| `historico_aluno` | admin | busca o histórico de matrículas de qualquer aluno |
| `disciplinas_com_vagas_aluno` | aluno | turmas ativas com vagas ordenadas de mais para menos |
| `meu_historico` | aluno | histórico de matrículas do aluno logado |

### `apps/core/`

Código de suporte e comando de seed do banco de dados.

```bash
docker compose run --rm web python manage.py seed
```

---

## Docker

### `Dockerfile`

Constrói o ambiente Python, instala dependências do sistema e Python, copia o projeto.

### `docker-compose.yml`

| Serviço | Descrição |
|---|---|
| `db` | PostgreSQL 16 |
| `web` | Aplicação Django |

### `entrypoint.sh`

1. Aguarda o PostgreSQL
2. `makemigrations`
3. `migrate`
4. `seed` (se `SEED_DB=True`)
5. Inicia o servidor de desenvolvimento

---

## Comandos úteis

```bash
# Iniciar o projeto
docker compose up --build

# Iniciar em modo detached
docker compose up -d --build

# Parar os containers
docker compose down

# Ver logs
docker compose logs -f web

# Gerar migrations
docker compose run --rm web python manage.py makemigrations

# Aplicar migrations
docker compose run --rm web python manage.py migrate

# Executar seed
docker compose run --rm web python manage.py seed

# Criar superusuário
docker compose run --rm web python manage.py createsuperuser
```

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · Django 5 |
| Banco de dados | PostgreSQL 16 |
| Frontend | HTML · CSS · Bootstrap 5 · Bootstrap Icons |
| Infraestrutura | Docker · Docker Compose |

---

## Autores

- Fláira Hanny Bomfim dos Santos
- Gabriel Gustavo Santos Queiroz
- Gabriel Lopes Aguiar

> Universidade Estadual do Sudoeste da Bahia — Bacharelado em Ciência da Computação · 2026
