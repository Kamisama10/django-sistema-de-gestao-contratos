from django.db import models

# Create your models here.

class Empresa(models.Model):
    AREAS = [
        ('mineracao',  'Mineração'),
        ('logistica',  'Logística'),
        ('energia',    'Energia'),
        ('engenharia', 'Engenharia'),
        ('outros',     'Outros'),
    ]

    razao_social    = models.CharField(max_length=200)
    nome_fantasia   = models.CharField(max_length=200, blank=True)
    cnpj            = models.CharField(max_length=18, unique=True)
    area_atuacao    = models.CharField(max_length=20, choices=AREAS)
    email           = models.EmailField(blank=True)
    telefone        = models.CharField(max_length=20, blank=True)
    endereco        = models.TextField(blank=True)
    ativa           = models.BooleanField(default=True)
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering            = ['razao_social']

    def __str__(self):
        return f'{self.razao_social} ({self.cnpj})'
