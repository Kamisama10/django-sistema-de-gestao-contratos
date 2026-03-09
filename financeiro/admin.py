from django.contrib import admin
from .models import Medicao, GastoOperacional

@admin.register(Medicao)
class MedicaoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'competencia', 'valor_bruto',
                    'valor_liquido', 'status']
    list_filter  = ['status']

@admin.register(GastoOperacional)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['contrato', 'competencia', 'categoria',
                    'subcategoria', 'valor', 'tipo']
    list_filter  = ['categoria', 'tipo']
