from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
from .models import CargoObrigatorio, ColaboradorMobilizado, Habilitacao
from .forms import CargoObrigatorioForm, ColaboradorForm, HabilitacaoForm
from contratos.models import Contrato
from django.http import HttpResponse
from utils.exportar import pdf_mobilizacao, excel_mobilizacao


# ── Painel geral de mobilização ───────────────────────────────────────────────
@login_required
def painel(request):
    hoje = date.today()

    # Todos os cargos de contratos vigentes
    cargos = CargoObrigatorio.objects.filter(
        contrato__status='vigente'
    ).select_related('contrato', 'contrato__empresa').order_by(
        'contrato__numero_sap', 'funcao'
    )

    # Separar por situação
    criticos  = [c for c in cargos if c.situacao == 'critico']
    alertas   = [c for c in cargos if c.situacao == 'alerta']
    regulares = [c for c in cargos if c.situacao == 'ok']

    # Habilitações vencidas ou vencendo em 30 dias
    hab_vencidas = Habilitacao.objects.filter(
        colaborador__status='mobilizado',
        data_validade__lt=hoje
    ).select_related('colaborador', 'colaborador__contrato')

    hab_vencendo = Habilitacao.objects.filter(
        colaborador__status='mobilizado',
        data_validade__gte=hoje,
        data_validade__lte=hoje + timedelta(days=30)
    ).select_related('colaborador', 'colaborador__contrato')

    # Colaboradores afastados sem substituto
    afastados = ColaboradorMobilizado.objects.filter(
        status__in=['afastado', 'ferias'],
        contrato__status='vigente'
    ).select_related('contrato', 'cargo_obrigatorio')

    context = {
        'criticos':    criticos,
        'alertas':     alertas,
        'regulares':   regulares,
        'total_criticos':  len(criticos),
        'total_alertas':   len(alertas),
        'total_regulares': len(regulares),
        'hab_vencidas':  hab_vencidas,
        'hab_vencendo':  hab_vencendo,
        'afastados':     afastados,
        'hoje':          hoje,
    }
    return render(request, 'mobilizacao/painel.html', context)


# ── Quadro de um contrato específico ─────────────────────────────────────────
@login_required
def quadro_contrato(request, contrato_pk):
    contrato      = get_object_or_404(Contrato, pk=contrato_pk)
    cargos        = contrato.cargos_obrigatorios.all()
    colaboradores = contrato.colaboradores.select_related(
        'cargo_obrigatorio'
    ).order_by('status', 'nome_completo')

    context = {
        'contrato':     contrato,
        'cargos':       cargos,
        'colaboradores': colaboradores,
    }
    return render(request, 'mobilizacao/quadro.html', context)


# ── Cargo obrigatório ─────────────────────────────────────────────────────────
@login_required
def cargo_criar(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    if request.method == 'POST':
        form = CargoObrigatorioForm(request.POST)
        if form.is_valid():
            cargo          = form.save(commit=False)
            cargo.contrato = contrato
            cargo.save()
            messages.success(request, f'Cargo "{cargo.funcao}" adicionado ao quadro obrigatório.')
            return redirect('mobilizacao:quadro', contrato_pk=contrato.pk)
    else:
        form = CargoObrigatorioForm()

    return render(request, 'mobilizacao/form_cargo.html', {
        'form':     form,
        'contrato': contrato,
        'titulo':   'Novo Cargo Obrigatório',
    })


@login_required
def cargo_editar(request, pk):
    cargo    = get_object_or_404(CargoObrigatorio, pk=pk)
    contrato = cargo.contrato
    if request.method == 'POST':
        form = CargoObrigatorioForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cargo "{cargo.funcao}" atualizado.')
            return redirect('mobilizacao:quadro', contrato_pk=contrato.pk)
    else:
        form = CargoObrigatorioForm(instance=cargo)

    return render(request, 'mobilizacao/form_cargo.html', {
        'form':     form,
        'contrato': contrato,
        'cargo':    cargo,
        'titulo':   f'Editar Cargo — {cargo.funcao}',
    })


# ── Colaborador ───────────────────────────────────────────────────────────────
@login_required
def colaborador_criar(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colab          = form.save(commit=False)
            colab.contrato = contrato
            colab.save()
            messages.success(request, f'{colab.nome_completo} mobilizado com sucesso!')
            return redirect('mobilizacao:quadro', contrato_pk=contrato.pk)
    else:
        form = ColaboradorForm()
        # Limita os cargos ao contrato atual
        form.fields['cargo_obrigatorio'].queryset = \
            CargoObrigatorio.objects.filter(contrato=contrato)

    return render(request, 'mobilizacao/form_colaborador.html', {
        'form':     form,
        'contrato': contrato,
        'titulo':   'Mobilizar Colaborador',
    })


@login_required
def colaborador_editar(request, pk):
    colab    = get_object_or_404(ColaboradorMobilizado, pk=pk)
    contrato = colab.contrato
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colab)
        if form.is_valid():
            form.save()
            messages.success(request, f'{colab.nome_completo} atualizado.')
            return redirect('mobilizacao:quadro', contrato_pk=contrato.pk)
    else:
        form = ColaboradorForm(instance=colab)
        form.fields['cargo_obrigatorio'].queryset = \
            CargoObrigatorio.objects.filter(contrato=contrato)

    return render(request, 'mobilizacao/form_colaborador.html', {
        'form':     form,
        'contrato': contrato,
        'colab':    colab,
        'titulo':   f'Editar — {colab.nome_completo}',
    })


@login_required
def colaborador_detalhe(request, pk):
    colab        = get_object_or_404(
        ColaboradorMobilizado.objects.select_related(
            'contrato', 'cargo_obrigatorio'
        ), pk=pk
    )
    habilitacoes = colab.habilitacoes.all()
    hoje         = date.today()

    context = {
        'colab':        colab,
        'habilitacoes': habilitacoes,
        'hoje':         hoje,
    }
    return render(request, 'mobilizacao/colaborador_detalhe.html', context)


# ── Habilitação ───────────────────────────────────────────────────────────────
@login_required
def habilitacao_criar(request, colaborador_pk):
    colab = get_object_or_404(ColaboradorMobilizado, pk=colaborador_pk)
    if request.method == 'POST':
        form = HabilitacaoForm(request.POST, request.FILES)
        if form.is_valid():
            hab             = form.save(commit=False)
            hab.colaborador = colab
            hab.save()
            messages.success(request, f'Habilitação "{hab.descricao}" registrada.')
            return redirect('mobilizacao:colaborador_detalhe', pk=colab.pk)
    else:
        form = HabilitacaoForm()

    return render(request, 'mobilizacao/form_habilitacao.html', {
        'form':  form,
        'colab': colab,
        'titulo': f'Nova Habilitação — {colab.nome_completo}',
    })


@login_required
def exportar_mobilizacao_pdf(request, contrato_pk):
    contrato     = get_object_or_404(Contrato, pk=contrato_pk)
    cargos       = contrato.cargos_obrigatorios.all()
    colaboradores = contrato.colaboradores.filter(
        status='mobilizado'
    ).order_by('nome_completo')
    buf  = pdf_mobilizacao(contrato, cargos, colaboradores)
    nome = f'Mobilizacao_{contrato.numero_sap}.pdf'
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{nome}"'
    return resp

@login_required
def exportar_mobilizacao_excel(request, contrato_pk):
    contrato      = get_object_or_404(Contrato, pk=contrato_pk)
    cargos        = contrato.cargos_obrigatorios.all()
    colaboradores = contrato.colaboradores.filter(
        status='mobilizado'
    ).order_by('nome_completo')
    buf  = excel_mobilizacao(contrato, cargos, colaboradores)
    nome = f'Mobilizacao_{contrato.numero_sap}.xlsx'
    resp = HttpResponse(
        buf,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    resp['Content-Disposition'] = f'attachment; filename="{nome}"'
    return resp
