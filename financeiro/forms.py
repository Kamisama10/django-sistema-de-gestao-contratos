from django import forms
from .models import Medicao, GastoOperacional


class MedicaoForm(forms.ModelForm):
    class Meta:
        model  = Medicao
        fields = [
            'numero', 'competencia', 'valor_bruto',
            'valor_glosa', 'valor_retencao', 'status',
            'data_submissao', 'data_aprovacao',
            'data_emissao_nf', 'data_pagamento',
            'data_previsao_pagamento', 'numero_nf',
            'justificativa_glosa', 'documento',
        ]
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1
            }),
            'competencia': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'valor_bruto': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
                'placeholder': '0,00'
            }),
            'valor_glosa': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
                'placeholder': '0,00'
            }),
            'valor_retencao': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
                'placeholder': '0,00'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_submissao': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_aprovacao': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_emissao_nf': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_pagamento': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_previsao_pagamento': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'numero_nf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da Nota Fiscal'
            }),
            'justificativa_glosa': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Descreva o motivo da glosa...'
            }),
            'documento': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero':                 'Número do BM',
            'competencia':            'Competência (mês de referência)',
            'valor_bruto':            'Valor Bruto (R$)',
            'valor_glosa':            'Valor da Glosa (R$)',
            'valor_retencao':         'Valor de Retenções (R$)',
            'status':                 'Status',
            'data_submissao':         'Data de Submissão',
            'data_aprovacao':         'Data de Aprovação',
            'data_emissao_nf':        'Data de Emissão da NF',
            'data_pagamento':         'Data de Pagamento',
            'data_previsao_pagamento':'Previsão de Pagamento',
            'numero_nf':              'Número da NF',
            'justificativa_glosa':    'Justificativa da Glosa',
            'documento':              'Documento (PDF)',
        }


class GastoForm(forms.ModelForm):
    class Meta:
        model  = GastoOperacional
        fields = [
            'competencia', 'categoria', 'subcategoria',
            'descricao', 'fornecedor', 'numero_nf_fornecedor',
            'valor', 'tipo', 'data_lancamento', 'comprovante',
        ]
        widgets = {
            'competencia': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Salários Operadores, Combustível CAT 336'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Descrição detalhada do gasto...'
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor (opcional)'
            }),
            'numero_nf_fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'NF do fornecedor (opcional)'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
                'placeholder': '0,00'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data_lancamento': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'competencia':          'Competência (mês)',
            'categoria':            'Categoria',
            'subcategoria':         'Subcategoria',
            'descricao':            'Descrição',
            'fornecedor':           'Fornecedor',
            'numero_nf_fornecedor': 'NF do Fornecedor',
            'valor':                'Valor (R$)',
            'tipo':                 'Tipo',
            'data_lancamento':      'Data do Lançamento',
            'comprovante':          'Comprovante (PDF)',
        }