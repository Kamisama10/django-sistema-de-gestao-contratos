from django.urls import path
from . import views

app_name = 'empresas'

urlpatterns = [
    path('',               views.empresa_lista,   name='lista'),
    path('nova/',          views.empresa_criar,   name='criar'),
    path('<int:pk>/',      views.empresa_detalhe, name='detalhe'),
    path('<int:pk>/editar/', views.empresa_editar, name='editar'),
]