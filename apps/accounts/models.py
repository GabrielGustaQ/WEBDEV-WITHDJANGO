class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    nome = models.CharField(max_length=150)
    matricula = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    curso = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)