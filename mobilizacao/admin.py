from django.contrib import admin
from .models import CargoObrigatorio, ColaboradorMobilizado, Habilitacao

@admin.register(CargoObrigatorio)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['funcao', 'contrato', 'quantidade_minima',
                    'total_ativos', 'deficit', 'is_critico']

@admin.register(ColaboradorMobilizado)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'funcao', 'contrato', 'status']
    list_filter  = ['status']