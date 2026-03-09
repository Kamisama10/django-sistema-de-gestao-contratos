from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # DRE do contrato
    path('contrato/<int:contrato_pk>/dre/',
         views.dre_contrato,
         name='dre'),

    # Medições
    path('contrato/<int:contrato_pk>/medicao/nova/',
         views.medicao_criar,
         name='medicao_criar'),
    path('medicao/<int:pk>/editar/',
         views.medicao_editar,
         name='medicao_editar'),

    # Gastos
    path('contrato/<int:contrato_pk>/gasto/novo/',
         views.gasto_criar,
         name='gasto_criar'),
    path('gasto/<int:pk>/editar/',
         views.gasto_editar,
         name='gasto_editar'),
    path('contrato/<int:contrato_pk>/gastos/',
         views.gastos_lista,
         name='gastos_lista'),

     #exportacao adicionado em 06/03 as 16:22h
     path('contrato/<int:contrato_pk>/dre/pdf/',
     views.exportar_dre_pdf,   name='dre_pdf'),
     path('contrato/<int:contrato_pk>/dre/excel/',
     views.exportar_dre_excel, name='dre_excel'),
]

