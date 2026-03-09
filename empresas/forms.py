from django import forms
from .models import Empresa


class EmpresaForm(forms.ModelForm):
    class Meta:
        model  = Empresa
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj',
            'area_atuacao', 'email', 'telefone',
            'endereco', 'ativa',
        ]
        widgets = {
            'razao_social':  forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Razão social completa'
            }),
            'nome_fantasia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome fantasia (opcional)'
            }),
            'cnpj':          forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00'
            }),
            'area_atuacao':  forms.Select(attrs={'class': 'form-select'}),
            'email':         forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contato@empresa.com.br'
            }),
            'telefone':      forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'endereco':      forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Endereço completo...'
            }),
            'ativa':         forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'razao_social':  'Razão Social',
            'nome_fantasia': 'Nome Fantasia',
            'cnpj':          'CNPJ',
            'area_atuacao':  'Área de Atuação',
            'email':         'E-mail',
            'telefone':      'Telefone',
            'endereco':      'Endereço',
            'ativa':         'Empresa ativa',
        }