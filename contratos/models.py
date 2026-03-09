from django.db import models
from django.contrib.auth.models import User
from empresas.models import Empresa


class Contrato(models.Model):
    AREAS = [
        ('mineracao',  'Mineração'),
        ('logistica',  'Logística'),
        ('energia',    'Energia'),
        ('engenharia', 'Engenharia'),
    ]
    MODALIDADES = [
        ('servico',      'Prestação de Serviço'),
        ('fornecimento', 'Fornecimento'),
        ('misto',        'Misto'),
    ]
    STATUS = [
        ('minuta',    'Minuta'),
        ('aprovacao', 'Em Aprovação'),
        ('vigente',   'Vigente'),
        ('suspenso',  'Suspenso'),
        ('encerrado', 'Encerrado'),
    ]

    # Identificação
    numero_sap      = models.CharField(max_length=20, unique=True)
    objeto          = models.TextField()
    area            = models.CharField(max_length=20, choices=AREAS)
    modalidade      = models.CharField(max_length=20, choices=MODALIDADES)
    status          = models.CharField(max_length=20, choices=STATUS,
                                       default='minuta')

    # Relacionamentos
    empresa         = models.ForeignKey(Empresa, on_delete=models.PROTECT,
                                        related_name='contratos')
    gestor_tecnico  = models.ForeignKey(User, on_delete=models.PROTECT,
                                        related_name='contratos_tecnicos')
    gestor_admin    = models.ForeignKey(User, on_delete=models.PROTECT,
                                        related_name='contratos_admin')

    # Financeiro
    valor_original  = models.DecimalField(max_digits=15, decimal_places=2)
    valor_atual     = models.DecimalField(max_digits=15, decimal_places=2)

    # Datas
    data_assinatura     = models.DateField()
    data_inicio         = models.DateField()
    data_termino        = models.DateField()
    data_termino_atual  = models.DateField()

    # Controle
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)
    criado_por      = models.ForeignKey(User, on_delete=models.PROTECT,
                                        related_name='contratos_criados',
                                        null=True)

    class Meta:
        verbose_name        = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering            = ['-criado_em']

    def __str__(self):
        return f'{self.numero_sap} — {self.empresa.razao_social}'

    @property
    def saldo_disponivel(self):
        total_medido = self.medicoes.filter(
            status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
        ).aggregate(total=models.Sum('valor_bruto'))['total'] or 0
        return self.valor_atual - total_medido

    @property
    def percentual_executado(self):
        if self.valor_atual > 0:
            executado = self.valor_atual - self.saldo_disponivel
            return round((executado / self.valor_atual) * 100, 1)
        return 0


class ItemEscopo(models.Model):
    contrato        = models.ForeignKey(Contrato, on_delete=models.CASCADE,
                                        related_name='itens')
    descricao       = models.TextField()
    unidade         = models.CharField(max_length=30)
    quantidade      = models.DecimalField(max_digits=12, decimal_places=3)
    preco_unitario  = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name        = 'Item de Escopo'
        verbose_name_plural = 'Itens de Escopo'

    def __str__(self):
        return f'{self.descricao} ({self.contrato.numero_sap})'

    @property
    def valor_total(self):
        return self.quantidade * self.preco_unitario


class Aditivo(models.Model):
    TIPOS = [
        ('prazo',       'Prazo'),
        ('valor',       'Valor'),
        ('prazo_valor', 'Prazo e Valor'),
    ]

    contrato            = models.ForeignKey(Contrato, on_delete=models.CASCADE,
                                            related_name='aditivos')
    numero              = models.PositiveIntegerField()
    tipo                = models.CharField(max_length=20, choices=TIPOS)
    nova_data_termino   = models.DateField(null=True, blank=True)
    valor_acrescimo     = models.DecimalField(max_digits=15, decimal_places=2,
                                              default=0)
    justificativa       = models.TextField()
    data_assinatura     = models.DateField()
    documento           = models.FileField(upload_to='aditivos/', blank=True)
    criado_em           = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Aditivo'
        verbose_name_plural = 'Aditivos'
        ordering            = ['numero']
        unique_together     = ['contrato', 'numero']

    def __str__(self):
        return f'{self.numero}º Aditivo — {self.contrato.numero_sap}'
