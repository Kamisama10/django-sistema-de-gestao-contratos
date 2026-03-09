from django import forms
from .models import CargoObrigatorio, ColaboradorMobilizado, Habilitacao


class CargoObrigatorioForm(forms.ModelForm):
    class Meta:
        model  = CargoObrigatorio
        fields = [
            'funcao', 'cbo', 'quantidade_minima',
            'is_critico', 'requer_habilitacao',
            'habilitacao_descricao', 'observacao',
        ]
        widgets = {
            'funcao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Técnico de Segurança do Trabalho'
            }),
            'cbo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 3516-05'
            }),
            'quantidade_minima': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1
            }),
            'is_critico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requer_habilitacao': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'habilitacao_descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: NR-10, NR-35, CREA ativo, CNH D'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Transcrição da cláusula contratual (opcional)...'
            }),
        }
        labels = {
            'funcao':                'Função / Cargo',
            'cbo':                   'CBO',
            'quantidade_minima':     'Quantidade Mínima Obrigatória',
            'is_critico':            'Cargo crítico (paralisa a obra se ausente)',
            'requer_habilitacao':    'Exige habilitação específica',
            'habilitacao_descricao': 'Habilitação exigida',
            'observacao':            'Observação / Cláusula contratual',
        }


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model  = ColaboradorMobilizado
        fields = [
            'cargo_obrigatorio', 'nome_completo', 'cpf',
            'matricula_empresa', 'funcao',
            'data_mobilizacao', 'data_desmobilizacao',
            'status', 'observacao',
        ]
        widgets = {
            'cargo_obrigatorio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do colaborador'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'matricula_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matrícula interna (opcional)'
            }),
            'funcao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Função exercida na obra'
            }),
            'data_mobilizacao': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_desmobilizacao': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Observações sobre o colaborador...'
            }),
        }
        labels = {
            'cargo_obrigatorio':   'Cargo Obrigatório Vinculado',
            'nome_completo':       'Nome Completo',
            'cpf':                 'CPF',
            'matricula_empresa':   'Matrícula',
            'funcao':              'Função na Obra',
            'data_mobilizacao':    'Data de Mobilização',
            'data_desmobilizacao': 'Data de Desmobilização',
            'status':              'Status',
            'observacao':          'Observação',
        }


class HabilitacaoForm(forms.ModelForm):
    class Meta:
        model  = Habilitacao
        fields = [
            'descricao', 'numero_registro',
            'data_emissao', 'data_validade', 'documento',
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: NR-10, NR-35, CNH D, CREA 123456/MG'
            }),
            'numero_registro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do registro ou certificado'
            }),
            'data_emissao': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'data_validade': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'documento': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'descricao':       'Habilitação / Certificação',
            'numero_registro': 'Número do Registro',
            'data_emissao':    'Data de Emissão',
            'data_validade':   'Data de Validade',
            'documento':       'Documento (PDF)',
        }