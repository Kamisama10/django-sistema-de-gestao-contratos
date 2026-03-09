from django.db import models
from django.contrib.auth.models import User
from contratos.models import Contrato, ItemEscopo
import json


class Medicao(models.Model):
    STATUS = [
        ('elaboracao', 'Em Elaboração'),
        ('submetida',  'Submetida à Vale'),
        ('em_analise', 'Em Análise'),
        ('aprovada',   'Aprovada'),
        ('glosada',    'Aprovada com Glosa'),
        ('rejeitada',  'Rejeitada'),
        ('nf_emitida', 'Nota Fiscal Emitida'),
        ('paga',       'Paga'),
    ]

    contrato                = models.ForeignKey(Contrato,
                                                on_delete=models.PROTECT,
                                                related_name='medicoes')
    numero                  = models.PositiveIntegerField()
    competencia             = models.DateField()
    valor_bruto             = models.DecimalField(max_digits=15, decimal_places=2,
                                                  default=0)
    valor_glosa             = models.DecimalField(max_digits=15, decimal_places=2,
                                                  default=0)
    valor_retencao          = models.DecimalField(max_digits=15, decimal_places=2,
                                                  default=0)
    status                  = models.CharField(max_length=20, choices=STATUS,
                                               default='elaboracao')
    data_submissao          = models.DateField(null=True, blank=True)
    data_aprovacao          = models.DateField(null=True, blank=True)
    data_emissao_nf         = models.DateField(null=True, blank=True)
    data_pagamento          = models.DateField(null=True, blank=True)
    data_previsao_pagamento = models.DateField(null=True, blank=True)
    numero_nf               = models.CharField(max_length=20, blank=True)
    justificativa_glosa     = models.TextField(blank=True)
    documento               = models.FileField(upload_to='medicoes/', blank=True)
    criado_em               = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Medição'
        verbose_name_plural = 'Medições'
        ordering            = ['-competencia', '-numero']
        unique_together     = ['contrato', 'numero']

    def __str__(self):
        return f'BM-{self.numero:03d} — {self.contrato.numero_sap}'

    @property
    def valor_liquido(self):
        return self.valor_bruto - self.valor_glosa - self.valor_retencao


class GastoOperacional(models.Model):
    CATEGORIAS = [
        ('mao_de_obra',    'Mão de Obra'),
        ('equipamentos',   'Equipamentos'),
        ('materiais',      'Materiais'),
        ('subcontratados', 'Subcontratados'),
        ('administrativo', 'Administrativo'),
        ('outros',         'Outros'),
    ]
    TIPOS = [
        ('realizado',    'Realizado'),
        ('provisionado', 'Provisionado'),
    ]

    contrato        = models.ForeignKey(Contrato, on_delete=models.PROTECT,
                                        related_name='gastos')
    competencia     = models.DateField()
    categoria       = models.CharField(max_length=20, choices=CATEGORIAS)
    subcategoria    = models.CharField(max_length=100)
    descricao       = models.TextField()
    fornecedor      = models.CharField(max_length=200, blank=True)
    numero_nf_fornecedor = models.CharField(max_length=20, blank=True)
    valor           = models.DecimalField(max_digits=15, decimal_places=2)
    tipo            = models.CharField(max_length=15, choices=TIPOS,
                                       default='realizado')
    data_lancamento = models.DateField()
    lancado_por     = models.ForeignKey(User, on_delete=models.PROTECT)
    comprovante     = models.FileField(upload_to='gastos/', blank=True)

    class Meta:
        verbose_name        = 'Gasto Operacional'
        verbose_name_plural = 'Gastos Operacionais'
        ordering            = ['-competencia', '-data_lancamento']

    def __str__(self):
        return f'{self.get_categoria_display()} — R$ {self.valor} ({self.contrato.numero_sap})'