from django.db import models
from django.contrib.auth.models import User
from contratos.models import Contrato
from datetime import date


class CargoObrigatorio(models.Model):
    contrato            = models.ForeignKey(Contrato, on_delete=models.CASCADE,
                                            related_name='cargos_obrigatorios')
    funcao              = models.CharField(max_length=100)
    cbo                 = models.CharField(max_length=10, blank=True)
    quantidade_minima   = models.PositiveIntegerField()
    is_critico          = models.BooleanField(
        default=False,
        verbose_name='Cargo Crítico',
        help_text='Cargo crítico paralisa a obra se estiver em déficit'
    )
    requer_habilitacao  = models.BooleanField(default=False)
    habilitacao_descricao = models.CharField(max_length=200, blank=True)
    observacao          = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Cargo Obrigatório'
        verbose_name_plural = 'Cargos Obrigatórios'

    def __str__(self):
        return f'{self.funcao} (mín. {self.quantidade_minima}) — {self.contrato.numero_sap}'

    @property
    def total_ativos(self):
        return self.colaboradores.filter(
            status='mobilizado',
            data_desmobilizacao__isnull=True
        ).count()

    @property
    def deficit(self):
        return max(0, self.quantidade_minima - self.total_ativos)

    @property
    def situacao(self):
        if self.deficit == 0:
            return 'ok'
        if self.is_critico:
            return 'critico'
        return 'alerta'


class ColaboradorMobilizado(models.Model):
    STATUS = [
        ('mobilizado',    'Mobilizado — Ativo'),
        ('afastado',      'Afastado — Temporário'),
        ('ferias',        'Férias'),
        ('desmobilizado', 'Desmobilizado'),
        ('substituicao',  'Em Processo de Substituição'),
    ]

    contrato            = models.ForeignKey(Contrato, on_delete=models.CASCADE,
                                            related_name='colaboradores')
    cargo_obrigatorio   = models.ForeignKey(CargoObrigatorio,
                                            on_delete=models.SET_NULL,
                                            null=True, blank=True,
                                            related_name='colaboradores')
    nome_completo       = models.CharField(max_length=200)
    cpf                 = models.CharField(max_length=14)
    matricula_empresa   = models.CharField(max_length=30, blank=True)
    funcao              = models.CharField(max_length=100)
    data_mobilizacao    = models.DateField()
    data_desmobilizacao = models.DateField(null=True, blank=True)
    status              = models.CharField(max_length=20, choices=STATUS,
                                           default='mobilizado')
    observacao          = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Colaborador Mobilizado'
        verbose_name_plural = 'Colaboradores Mobilizados'
        ordering            = ['nome_completo']

    def __str__(self):
        return f'{self.nome_completo} — {self.funcao}'

    @property
    def esta_ativo(self):
        return self.status == 'mobilizado' and self.data_desmobilizacao is None


class Habilitacao(models.Model):
    colaborador     = models.ForeignKey(ColaboradorMobilizado,
                                        on_delete=models.CASCADE,
                                        related_name='habilitacoes')
    descricao       = models.CharField(max_length=200)
    numero_registro = models.CharField(max_length=100, blank=True)
    data_emissao    = models.DateField(null=True, blank=True)
    data_validade   = models.DateField(null=True, blank=True)
    documento       = models.FileField(upload_to='habilitacoes/', blank=True)

    class Meta:
        verbose_name        = 'Habilitação'
        verbose_name_plural = 'Habilitações'

    def __str__(self):
        return f'{self.descricao} — {self.colaborador.nome_completo}'

    @property
    def esta_vencida(self):
        if self.data_validade:
            return self.data_validade < date.today()
        return False

    @property
    def vence_em_breve(self):
        from datetime import timedelta
        if self.data_validade:
            return (not self.esta_vencida and
                    self.data_validade <= date.today() + timedelta(days=30))
        return False