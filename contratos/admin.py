from django.contrib import admin
from .models import Contrato, ItemEscopo, Aditivo


class ItemEscopoInline(admin.TabularInline):
    model   = ItemEscopo
    extra   = 1

class AditivoInline(admin.TabularInline):
    model   = Aditivo
    extra   = 0

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display    = ['numero_sap', 'empresa', 'area', 'status',
                       'valor_atual', 'data_termino_atual']
    list_filter     = ['status', 'area', 'modalidade']
    search_fields   = ['numero_sap', 'empresa__razao_social', 'objeto']
    inlines         = [ItemEscopoInline, AditivoInline]
