from django.urls import path
from . import views

app_name = 'mobilizacao'

urlpatterns = [
    # Painel geral
    path('',
         views.painel,
         name='painel'),

    # Quadro por contrato
    path('contrato/<int:contrato_pk>/',
         views.quadro_contrato,
         name='quadro'),

    # Cargos obrigatórios
    path('contrato/<int:contrato_pk>/cargo/novo/',
         views.cargo_criar,
         name='cargo_criar'),
    path('cargo/<int:pk>/editar/',
         views.cargo_editar,
         name='cargo_editar'),

    # Colaboradores
    path('contrato/<int:contrato_pk>/colaborador/novo/',
         views.colaborador_criar,
         name='colaborador_criar'),
    path('colaborador/<int:pk>/editar/',
         views.colaborador_editar,
         name='colaborador_editar'),
    path('colaborador/<int:pk>/',
         views.colaborador_detalhe,
         name='colaborador_detalhe'),

    # Habilitações
    path('colaborador/<int:colaborador_pk>/habilitacao/nova/',
         views.habilitacao_criar,
         name='habilitacao_criar'),

     # exportacao adicionado em 16:22h 06/03
     path('contrato/<int:contrato_pk>/exportar/pdf/',
     views.exportar_mobilizacao_pdf,   name='exportar_pdf'),
     path('contrato/<int:contrato_pk>/exportar/excel/',
     views.exportar_mobilizacao_excel, name='exportar_excel'),
]