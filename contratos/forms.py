from django import forms
from .models import Contrato, ItemEscopo, Aditivo


class ContratoForm(forms.ModelForm):
    class Meta:
        model  = Contrato
        fields = [
            'numero_sap', 'objeto', 'area', 'modalidade', 'status',
            'empresa', 'gestor_tecnico', 'gestor_admin',
            'valor_original', 'valor_atual',
            'data_assinatura', 'data_inicio',
            'data_termino', 'data_termino_atual',
        ]
        widgets = {
            'numero_sap':        forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 4500123456'
            }),
            'objeto':            forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Descreva o objeto do contrato...'
            }),
            'area':              forms.Select(attrs={'class': 'form-select'}),
            'modalidade':        forms.Select(attrs={'class': 'form-select'}),
            'status':            forms.Select(attrs={'class': 'form-select'}),
            'empresa':           forms.Select(attrs={'class': 'form-select'}),
            'gestor_tecnico':    forms.Select(attrs={'class': 'form-select'}),
            'gestor_admin':      forms.Select(attrs={'class': 'form-select'}),
            'valor_original':    forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0,00'
            }),
            'valor_atual':       forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0,00'
            }),
            'data_assinatura':   forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_inicio':       forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_termino':      forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_termino_atual': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
        }
        labels = {
            'numero_sap':         'Número SAP',
            'objeto':             'Objeto do Contrato',
            'area':               'Área',
            'modalidade':         'Modalidade',
            'status':             'Status',
            'empresa':            'Empresa Contratada',
            'gestor_tecnico':     'Gestor Técnico',
            'gestor_admin':       'Gestor Administrativo',
            'valor_original':     'Valor Original (R$)',
            'valor_atual':        'Valor Atual (R$)',
            'data_assinatura':    'Data de Assinatura',
            'data_inicio':        'Data de Início',
            'data_termino':       'Data de Término Original',
            'data_termino_atual': 'Data de Término Atual',
        }


class ItemEscopoForm(forms.ModelForm):
    class Meta:
        model  = ItemEscopo
        fields = ['descricao', 'unidade', 'quantidade', 'preco_unitario']
        widgets = {
            'descricao':      forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Descrição do item...'
            }),
            'unidade':        forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: m³, h, un, km'
            }),
            'quantidade':     forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.001'
            }),
            'preco_unitario': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
        }
        labels = {
            'descricao':      'Descrição',
            'unidade':        'Unidade',
            'quantidade':     'Quantidade',
            'preco_unitario': 'Preço Unitário (R$)',
        }


class AditivoForm(forms.ModelForm):
    class Meta:
        model  = Aditivo
        fields = [
            'numero', 'tipo', 'nova_data_termino',
            'valor_acrescimo', 'justificativa',
            'data_assinatura', 'documento',
        ]
        widgets = {
            'numero':            forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo':              forms.Select(attrs={'class': 'form-select'}),
            'nova_data_termino': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'valor_acrescimo':   forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'justificativa':     forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Justificativa formal do aditivo...'
            }),
            'data_assinatura':   forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'documento':         forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero':            'Número do Aditivo',
            'tipo':              'Tipo',
            'nova_data_termino': 'Nova Data de Término',
            'valor_acrescimo':   'Valor de Acréscimo (R$)',
            'justificativa':     'Justificativa',
            'data_assinatura':   'Data de Assinatura',
            'documento':         'Documento (PDF)',
        }