# Seminário — Django na Prática

> Material de apoio para apresentação do framework Django usando o projeto **Sistema de Pré-Matrícula Acadêmica** como exemplo real.

---

## 1. O que é Django?

Django é um framework web de alto nível escrito em Python que encoraja o desenvolvimento rápido e um design limpo e pragmático. Foi criado em 2003 pela equipe do jornal Lawrence Journal-World e lançado como open-source em 2005.

**Filosofia central: "batteries included"** — autenticação, ORM, painel admin, sistema de templates, proteção CSRF e muito mais já vêm prontos, sem precisar instalar pacotes de terceiros para o básico.

Outros princípios do Django:

| Princípio | O que significa |
|---|---|
| DRY *(Don't Repeat Yourself)* | Escreva a lógica uma vez; o framework a reutiliza |
| Explícito > implícito | Configurações declaradas, sem mágica escondida |
| Loose coupling | Cada camada (model, view, template) pode ser trocada independentemente |
| Segurança por padrão | CSRF, SQL injection e XSS protegidos automaticamente |

---

## 2. Arquitetura MTV

Django segue o padrão **MTV** — uma variação do MVC tradicional:

```
Requisição HTTP
      │
      ▼
  urls.py          ← roteador: qual view responde a qual URL?
      │
      ▼
  views.py         ← Controller: orquestra a lógica de negócio
      │         │
      │         └──► models.py  ← Model: define as tabelas e regras de dados
      │
      ▼
 templates/        ← Template (View no MVC): HTML com linguagem de template
      │
      ▼
Resposta HTTP
```

**No projeto:**

```
config/urls.py  →  apps/*/views.py  →  apps/*/models.py
                                    →  templates/**/*.html
```

---

## 3. Estrutura de um projeto Django

### 3.1 Projeto vs. Apps

Um **projeto** Django é o contêiner principal com as configurações globais. Dentro dele vivem uma ou mais **apps** — módulos independentes e reutilizáveis, cada um responsável por um domínio.

```
WEBDEV-WITHDJANGO/        ← projeto
├── config/               ← configurações globais (settings, urls, wsgi)
└── apps/
    ├── accounts/         ← app: autenticação e perfis
    ├── alunos/           ← app: cadastro de alunos
    ├── disciplinas/      ← app: disciplinas e turmas
    ├── matriculas/       ← app: operações de matrícula
    ├── relatorios/       ← app: relatórios somente leitura
    └── core/             ← app: utilitários e seed
```

### 3.2 Arquivos gerados pelo `startapp`

Ao criar uma app com `python manage.py startapp nome`, o Django gera:

| Arquivo | Papel |
|---|---|
| `models.py` | Define os modelos (tabelas do banco) |
| `views.py` | Lógica de cada página/endpoint |
| `urls.py` | Rotas específicas da app (incluídas no `config/urls.py`) |
| `forms.py` | Formulários com validação (criado manualmente quando necessário) |
| `admin.py` | Registra modelos no painel `/admin/` |
| `apps.py` | Configuração da app (nome, label) |
| `migrations/` | Histórico versionado do schema do banco |

---

## 4. Arquivos de configuração essenciais

### 4.1 `config/settings.py`

Central de configuração do projeto. Os pontos mais importantes:

```python
# Leitura de variáveis de ambiente via python-decouple
# (mantém segredos fora do código-fonte)
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

# Apps instaladas — todas as apps do projeto precisam estar aqui
INSTALLED_APPS = [
    # apps nativas do Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # apps do projeto
    "apps.core",
    "apps.accounts",
    "apps.alunos",
    "apps.disciplinas",
    "apps.matriculas",
    "apps.relatorios",
]

# Middlewares: camadas que processam cada requisição/resposta em ordem
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",      # proteção CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Localização
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Bahia"

# Onde o Django encontra os templates
TEMPLATES = [{
    "DIRS": [BASE_DIR / "templates"],  # pasta global de templates
    "APP_DIRS": True,                  # também busca em cada app/templates/
}]

# Banco de dados
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DATABASE_NAME"),
        ...
    }
}

# Redirecionar para login quando @login_required bloquear
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
```

**Por que variáveis de ambiente?** O arquivo `.env` não é versionado, então credenciais reais nunca aparecem no git. `python-decouple` lê essas variáveis automaticamente.

### 4.2 `config/urls.py`

Roteador raiz do projeto. Cada app declara suas próprias rotas num `urls.py` local, e aqui fazemos o `include`:

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),           # painel nativo do Django
    path("", include("apps.accounts.urls")),   # login, logout, dashboard
    path("alunos/", include("apps.alunos.urls")),
    path("disciplinas/", include("apps.disciplinas.urls")),
    path("matriculas/", include("apps.matriculas.urls")),
    path("relatorios/", include("apps.relatorios.urls")),
]
```

Dentro de cada app:

```python
# apps/alunos/urls.py
urlpatterns = [
    path("",          views.aluno_list,   name="alunos_list"),
    path("novo/",     views.aluno_form,   name="alunos_create"),
    path("<int:pk>/", views.aluno_form,   name="alunos_edit"),
    path("<int:pk>/desativar/", views.aluno_desativar, name="alunos_desativar"),
]
```

O argumento `name=` permite referenciar a rota no template com `{% url 'alunos_list' %}` sem hardcodar o caminho.

---

## 5. Models — mapeamento objeto-relacional (ORM)

### 5.1 Conceito

O ORM do Django mapeia cada classe Python para uma tabela SQL. Não é necessário escrever SQL na mão para operações comuns.

### 5.2 Exemplos do projeto

**`Aluno`** — tabela de estudantes:

```python
# apps/alunos/models.py
class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="aluno")
    nome = models.CharField(max_length=150)
    matricula = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    curso = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)   # preenchido na criação
    atualizado_em = models.DateTimeField(auto_now=True)   # atualizado a cada save()

    class Meta:
        ordering = ["nome"]   # ordem padrão de qualquer queryset

    def __str__(self):
        return f"{self.nome} - {self.matricula}"
```

**`Turma`** — restrição de unicidade declarada no model:

```python
# apps/disciplinas/models.py
class Turma(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name="turmas")
    periodo_letivo = models.CharField(max_length=20)
    vagas_total = models.PositiveIntegerField()
    vagas_disponiveis = models.PositiveIntegerField()
    ativa = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["disciplina", "periodo_letivo"],
                name="uniq_turma_disciplina_periodo",
            )
        ]

    @property
    def vagas_ocupadas(self):                      # propriedade calculada, não coluna
        return self.vagas_total - self.vagas_disponiveis

    def clean(self):                               # validação a nível de model
        if self.vagas_disponiveis > self.vagas_total:
            raise ValidationError("Vagas disponíveis não podem exceder o total.")
```

**`Matricula`** — restrição condicional (ignora canceladas):

```python
# apps/matriculas/models.py
class Matricula(models.Model):
    STATUS_CONFIRMADA = "confirmada"
    STATUS_PENDENTE   = "pendente"
    STATUS_CANCELADA  = "cancelada"

    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT, related_name="matriculas")
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name="matriculas")
    status = models.CharField(max_length=20, choices=[...], default=STATUS_CONFIRMADA)
    criada_em = models.DateTimeField(auto_now_add=True)
    cancelada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # Um aluno não pode ter duas matrículas ativas na mesma turma
            models.UniqueConstraint(
                fields=["aluno", "turma"],
                condition=~Q(status="cancelada"),
                name="uniq_matricula_ativa_por_turma",
            )
        ]
```

### 5.3 Migrations

Após criar ou modificar um model, dois comandos sincronizam o banco:

```bash
python manage.py makemigrations   # gera o arquivo de migração em migrations/
python manage.py migrate          # aplica as migrações pendentes no banco
```

Os arquivos em `migrations/` são versionados no git — eles documentam a evolução do schema ao longo do tempo.

---

## 6. Views — a lógica da aplicação

### 6.1 Function-based views (FBV)

O projeto usa FBVs por serem diretas e fáceis de ler.

**View simples com autenticação e controle de perfil:**

```python
# apps/accounts/views.py
from django.contrib.auth.decorators import login_required

@login_required          # redireciona para /login/ se não autenticado
def dashboard(request):
    perfil = obter_ou_criar_perfil(request.user)
    context = {"perfil": perfil}

    if perfil.is_aluno and hasattr(request.user, "aluno"):
        from apps.matriculas.models import Matricula
        aluno = request.user.aluno
        matriculas = Matricula.objects.filter(aluno=aluno)
        context["total_matriculas"] = matriculas.count()
        context["confirmadas"]      = matriculas.filter(status=Matricula.STATUS_CONFIRMADA).count()
        context["pendentes"]        = matriculas.filter(status=Matricula.STATUS_PENDENTE).count()

    return render(request, "dashboard.html", context)
```

**Controle de acesso por perfil com `user_passes_test`:**

```python
# helper que define a regra
def usuario_secretaria(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.is_staff or
        (hasattr(user, "perfil") and user.perfil.tipo == PerfilUsuario.Tipo.SECRETARIA)
    )

# decorador aplicado na view
@user_passes_test(usuario_secretaria)
def aluno_list(request):
    ...
```

### 6.2 Lógica de negócio em services

Para evitar que views fiquem gordas, a lógica crítica de matrícula vive em `services.py`:

```python
# apps/matriculas/services.py
from django.db import transaction

@transaction.atomic                          # tudo ou nada
def realizar_matricula(aluno, turma):
    turma = Turma.objects.select_for_update().get(pk=turma.pk)  # lock otimista
    # validações ...
    matricula = Matricula.objects.create(aluno=aluno, turma=turma, status="confirmada")
    turma.vagas_disponiveis -= 1
    turma.save(update_fields=["vagas_disponiveis"])
    return matricula
```

`select_for_update()` trava a linha no banco durante a transação, impedindo que dois usuários ocupem a última vaga simultaneamente.

---

## 7. Templates

### 7.1 Herança de templates

O arquivo `templates/base.html` define o esqueleto HTML completo (sidebar, topbar, mensagens flash, scripts). Cada página herda dele e sobrescreve apenas o que muda:

```html
<!-- templates/base.html -->
{% block title %}Pré-Matrícula Acadêmica{% endblock %}
...
{% block page_title %}Sistema de Pré-Matrícula{% endblock %}
...
<section class="content-card">
    {% block content %}{% endblock %}   <!-- slot para o conteúdo de cada página -->
</section>
```

```html
<!-- templates/dashboard.html -->
{% extends "base.html" %}

{% block title %}Dashboard | Pré-Matrícula{% endblock %}
{% block page_title %}Dashboard{% endblock %}
{% block page_subtitle %}Resumo das principais operações do sistema{% endblock %}

{% block content %}
  <!-- conteúdo específico do dashboard -->
{% endblock %}
```

### 7.2 Tags e filtros úteis

| Tag / filtro | Uso no projeto |
|---|---|
| `{% url 'nome' %}` | Gera URL pelo name da rota: `{% url 'alunos_list' %}` |
| `{% if user.perfil.is_secretaria %}` | Renderização condicional por perfil |
| `{% for m in matriculas %}` | Laço sobre queryset passado pela view |
| `{% csrf_token %}` | Proteção obrigatória em todo `<form method="post">` |
| `{% load static %}` + `{% static 'css/style.css' %}` | Referência a arquivos estáticos |
| `{% block nome %}{% endblock %}` | Define slot substituível na herança |
| `{{ user.get_full_name\|default:user.username }}` | Filtro com valor padrão |

### 7.3 Mensagens flash

O Django armazena mensagens na sessão para exibir feedback após um redirect (padrão PRG — Post/Redirect/Get). Em `base.html`:

```html
{% if messages %}
  {% for message in messages %}
    <div class="alert alert-{{ message.tags }}">{{ message }}</div>
  {% endfor %}
{% endif %}
```

Na view:

```python
messages.success(request, "Senha alterada com sucesso.")
return redirect("dashboard")
```

---

## 8. Formulários

Django gera formulários HTML e faz a validação automaticamente a partir de uma classe Python:

```python
# apps/alunos/forms.py
from django import forms
from .models import Aluno

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ["nome", "matricula", "email", "curso", "telefone"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
        }
```

Na view:

```python
def aluno_form(request, pk=None):
    aluno = get_object_or_404(Aluno, pk=pk) if pk else None
    form = AlunoForm(request.POST or None, instance=aluno)
    if form.is_valid():
        form.save()
        return redirect("alunos_list")
    return render(request, "alunos/form.html", {"form": form})
```

No template:

```html
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}         {# ou campo por campo: {{ form.nome }} #}
  <button type="submit">Salvar</button>
</form>
```

---

## 9. Autenticação — o que o Django já entrega

O Django inclui um sistema de autenticação completo:

| Recurso | Como o projeto usa |
|---|---|
| `User` model | Tabela `auth_user`, base de todos os usuários |
| `login` / `logout` | `auth_login(request, user)` e `auth_logout(request)` |
| `@login_required` | Decorator que bloqueia views para não autenticados |
| `user_passes_test` | Autorização por regra customizada (secretaria vs. aluno) |
| `update_session_auth_hash` | Mantém sessão ativa após troca de senha |
| CSRF | `{% csrf_token %}` em todo formulário POST |

O projeto estende o `User` padrão com `PerfilUsuario` (OneToOne), adicionando o campo `tipo` sem reescrever o sistema de auth do Django.

---

## 10. ORM na prática — exemplos de queries

```python
# Todos os alunos ativos, ordenados por nome
Aluno.objects.filter(ativo=True)

# Matrículas confirmadas de um aluno específico
Matricula.objects.filter(aluno=aluno, status="confirmada")

# Turmas com vagas, ordenadas de mais vagas para menos
Turma.objects.filter(ativa=True, vagas_disponiveis__gt=0).order_by("-vagas_disponiveis")

# Eager loading: busca disciplina junto com a turma (evita N+1)
Turma.objects.select_related("disciplina").filter(ativa=True)

# Contagens agrupadas por disciplina
from django.db.models import Count
Disciplina.objects.annotate(total_matriculas=Count("turmas__matriculas"))

# Lock otimista para operações concorrentes
Turma.objects.select_for_update().get(pk=turma_id)
```

---

## 11. Painel de administração

Com apenas duas linhas por model, o Django disponibiliza um CRUD completo em `/admin/`:

```python
# apps/alunos/admin.py
from django.contrib import admin
from .models import Aluno

admin.site.register(Aluno)
```

Para customizar a listagem:

```python
@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ["nome", "matricula", "curso", "ativo"]
    search_fields = ["nome", "matricula", "email"]
    list_filter = ["ativo", "curso"]
```

---

## 12. Comando de gerenciamento customizado

O Django permite criar comandos executáveis via `manage.py`. O projeto usa isso para popular o banco com dados de teste:

```python
# apps/core/management/commands/seed.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Popula o banco com dados de teste"

    def handle(self, *args, **options):
        # cria usuários, alunos, disciplinas, turmas e matrículas
        self.stdout.write(self.style.SUCCESS("Seed concluído!"))
```

Executado via:

```bash
python manage.py seed
# ou via Docker:
docker compose run --rm web python manage.py seed
```

---

## 13. Docker no projeto

O projeto é 100% containerizado, o que resolve o clássico "na minha máquina funciona":

```yaml
# docker-compose.yml (simplificado)
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: prematricula
      ...

  web:
    build: .
    ports:
      - "8001:8000"
    depends_on:
      - db
    env_file: .env
    command: ./entrypoint.sh   # aguarda o db, migra, seed, runserver
```

O `entrypoint.sh` coordena a inicialização:

```bash
# Aguarda PostgreSQL
until pg_isready -h "$DATABASE_HOST"; do sleep 1; done

python manage.py makemigrations
python manage.py migrate

if [ "$SEED_DB" = "True" ]; then
    python manage.py seed
fi

python manage.py runserver 0.0.0.0:8000
```

---

## 14. Fluxo completo de uma requisição

**Exemplo: aluno acessa "Minhas Matrículas"**

```
1. Browser  →  GET /matriculas/minhas/

2. config/urls.py
      path("matriculas/", include("apps.matriculas.urls"))

3. apps/matriculas/urls.py
      path("minhas/", views.minhas_matriculas, name="minhas_matriculas")

4. apps/matriculas/views.py
      @login_required
      @user_passes_test(usuario_aluno)
      def minhas_matriculas(request):
          aluno = request.user.aluno
          matriculas = Matricula.objects.filter(aluno=aluno).select_related("turma__disciplina")
          return render(request, "matriculas/list.html", {"matriculas": matriculas})

5. ORM  →  SELECT ... FROM matriculas_matricula WHERE aluno_id = ?

6. templates/matriculas/list.html
      {% extends "base.html" %}
      {% block content %}
          {% for m in matriculas %} ... {% endfor %}
      {% endblock %}

7. Browser  ←  HTML renderizado com a lista de matrículas
```

---

## 15. Pontos de destaque para apresentação

- **Sem SQL escrito à mão** — o ORM cuida de todas as queries comuns
- **Migrations versionadas** — o schema evolui com o código no git
- **Autenticação incluída** — login, sessão, CSRF, hash de senha fora da caixa
- **Template inheritance** — zero duplicação de HTML; mude o `base.html` e afeta todas as páginas
- **`select_for_update`** — evita condição de corrida na matrícula concorrente
- **Separação de responsabilidades** — models definem dados, services definem regras, views orquestram, templates apresentam
- **`manage.py`** — ferramenta única para migrations, seed, shell, testes e servidor de desenvolvimento

---

## Referências

- Documentação oficial: https://docs.djangoproject.com/
- Tutorial oficial (Polls app): https://docs.djangoproject.com/en/5.0/intro/tutorial01/
- Django ORM queries: https://docs.djangoproject.com/en/5.0/topics/db/queries/
- Deploy checklist: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
