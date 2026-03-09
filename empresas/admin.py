from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display    = ['razao_social', 'cnpj', 'area_atuacao', 'ativa']
    list_filter     = ['area_atuacao', 'ativa']
    search_fields   = ['razao_social', 'cnpj']
