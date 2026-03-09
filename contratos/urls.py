from django.urls import path
from . import views

app_name = 'contratos'

urlpatterns = [
    path('',                                    views.dashboard,       name='dashboard'),
    path('contratos/',                          views.contrato_lista,  name='lista'),
    path('contratos/novo/',                     views.contrato_criar,  name='criar'),
    path('contratos/<int:pk>/',                 views.contrato_detalhe,name='detalhe'),
    path('contratos/<int:pk>/editar/',          views.contrato_editar, name='editar'),
    path('contratos/<int:contrato_pk>/item/',   views.item_criar,      name='item_criar'),
    path('contratos/<int:contrato_pk>/aditivo/',views.aditivo_criar,   name='aditivo_criar'),
    path('exportar/pdf/',   views.exportar_contratos_pdf,   name='exportar_pdf'),
    path('exportar/excel/', views.exportar_contratos_excel, name='exportar_excel'),
]