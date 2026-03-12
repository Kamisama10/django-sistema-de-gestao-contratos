from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import Contrato, ItemEscopo, Aditivo
from .forms import ContratoForm, ItemEscopoForm, AditivoForm
from mobilizacao.models import CargoObrigatorio
from financeiro.models import Medicao, GastoOperacional
import json
from django.http import HttpResponse
from utils.exportar import pdf_contratos, excel_contratos


@login_required
def dashboard(request):
    hoje = date.today()

    # ── Contratos por status ──────────────────────────────────────────────
    contratos_vigentes  = Contrato.objects.filter(status='vigente')
    total_vigentes      = contratos_vigentes.count()
    total_suspensos     = Contrato.objects.filter(status='suspenso').count()
    total_encerrados    = Contrato.objects.filter(status='encerrado').count()
    total_aprovacao     = Contrato.objects.filter(status='aprovacao').count()

    # ── Valor total dos contratos vigentes ────────────────────────────────
    valor_total_carteira = contratos_vigentes.aggregate(
        total=Sum('valor_atual')
    )['total'] or 0

    # ── Contratos vencendo em breve ───────────────────────────────────────
    em_60_dias = contratos_vigentes.filter(
        data_termino_atual__lte=hoje + timedelta(days=60),
        data_termino_atual__gte=hoje
    ).order_by('data_termino_atual')

    # ── Alertas de mobilização (déficit de pessoal) ───────────────────────
    cargos_com_deficit = []
    for cargo in CargoObrigatorio.objects.filter(
        contrato__status='vigente'
    ).select_related('contrato', 'contrato__empresa'):
        if cargo.deficit > 0:
            cargos_com_deficit.append(cargo)

    alertas_criticos = [c for c in cargos_com_deficit if c.is_critico]
    alertas_normais  = [c for c in cargos_com_deficit if not c.is_critico]

    # ── Medições pendentes de pagamento ──────────────────────────────────
    medicoes_pendentes = Medicao.objects.filter(
        status__in=['aprovada', 'glosada', 'nf_emitida']
    ).select_related('contrato', 'contrato__empresa').order_by('data_previsao_pagamento')

    valor_a_receber = medicoes_pendentes.aggregate(
        total=Sum('valor_bruto')
    )['total'] or 0

    # ── DRE consolidado do mês atual ──────────────────────────────────────
    mes_atual       = hoje.replace(day=1)
    fat_mes         = Medicao.objects.filter(
        competencia=mes_atual,
        status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(total=Sum('valor_bruto'))['total'] or 0

    gastos_mes      = GastoOperacional.objects.filter(
        competencia=mes_atual,
        tipo='realizado'
    ).aggregate(total=Sum('valor'))['total'] or 0

    margem_mes      = fat_mes - gastos_mes
    margem_pct      = round((margem_mes / fat_mes * 100), 1) if fat_mes > 0 else 0

    # ── Gráfico: faturamento x gastos últimos 6 meses ─────────────────────
    labels, fat_data, gasto_data = [], [], []
    mes_base = hoje.replace(day=1)
    for i in range(5, -1, -1):
        # Subtrai i meses de forma precisa
        mes = mes_base.replace(day=1)
        total_mes = mes.month - i
        ano = mes.year + (total_mes - 1) // 12
        mes_num = ((total_mes - 1) % 12) + 1
        d = date(ano, mes_num, 1)

        f = Medicao.objects.filter(
            competencia=d,
            status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0
        g = GastoOperacional.objects.filter(
            competencia=d, tipo='realizado'
    ).aggregate(t=Sum('valor'))['t'] or 0
        labels.append(d.strftime('%b/%y'))
        fat_data.append(float(f))
        gasto_data.append(float(g))

    # ── Tabela de contratos vigentes ──────────────────────────────────────
    contratos_tabela = []
    for c in contratos_vigentes.select_related('empresa')[:20]:
        fat_contrato = Medicao.objects.filter(
            contrato=c,
            status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
        ).aggregate(t=Sum('valor_bruto'))['t'] or 0

        gastos_contrato = GastoOperacional.objects.filter(
            contrato=c, tipo='realizado'
        ).aggregate(t=Sum('valor'))['t'] or 0

        margem_c   = fat_contrato - gastos_contrato
        margem_c_p = round((margem_c / fat_contrato * 100), 1) if fat_contrato > 0 else 0

        dias_restantes = (c.data_termino_atual - hoje).days

        tem_alerta = any(
            cargo.deficit > 0
            for cargo in c.cargos_obrigatorios.all()
        )

        contratos_tabela.append({
            'contrato':        c,
            'faturamento':     fat_contrato,
            'gastos':          gastos_contrato,
            'margem':          margem_c,
            'margem_pct':      margem_c_p,
            'dias_restantes':  dias_restantes,
            'tem_alerta':      tem_alerta,
        })

    context = {
        # Cards de resumo
        'total_vigentes':      total_vigentes,
        'total_suspensos':     total_suspensos,
        'total_encerrados':    total_encerrados,
        'total_aprovacao':     total_aprovacao,
        'valor_total_carteira': valor_total_carteira,
        'valor_a_receber':     valor_a_receber,

        # DRE do mês
        'fat_mes':    fat_mes,
        'gastos_mes': gastos_mes,
        'margem_mes': margem_mes,
        'margem_pct': margem_pct,

        # Alertas
        'alertas_criticos': alertas_criticos,
        'alertas_normais':  alertas_normais,
        'em_60_dias':       em_60_dias,

        # Medições
        'medicoes_pendentes': medicoes_pendentes[:10],

        # Tabela de contratos
        'contratos_tabela': contratos_tabela,

        # Gráfico (JSON para o Chart.js)
        'chart_labels':    json.dumps(labels),
        'chart_fat':       json.dumps(fat_data),
        'chart_gastos':    json.dumps(gasto_data),

        'hoje': hoje,
    }

    return render(request, 'contratos/dashboard.html', context)


# ── Lista de Contratos ────────────────────────────────────────────────────────
@login_required
def contrato_lista(request):
    qs = Contrato.objects.select_related('empresa').all()

    # Filtros
    status = request.GET.get('status', '')
    area   = request.GET.get('area', '')
    busca  = request.GET.get('q', '')
    financeiro = request.GET.get('financeiro', '')

    if status:
        qs = qs.filter(status=status)
    if area:
        qs = qs.filter(area=area)
    if busca:
        qs = qs.filter(
            Q(numero_sap__icontains=busca) |
            Q(empresa__razao_social__icontains=busca) |
            Q(objeto__icontains=busca)
        )

    # Mensagem de orientação para seção financeira
    financeiro_labels = {
        'medicao': ('Medições', 'receipt-cutoff'),
        'gasto':   ('Gastos Operacionais', 'cash-stack'),
        'dre':     ('DRE Mensal', 'bar-chart-fill'),
    }
    financeiro_info = financeiro_labels.get(financeiro)

    context = {
        'contratos':        qs,
        'total':            qs.count(),
        'status_atual':     status,
        'area_atual':       area,
        'busca':            busca,
        'status_choices':   Contrato.STATUS,
        'area_choices':     Contrato.AREAS,
        'financeiro':       financeiro,
        'financeiro_info':  financeiro_info,
    }
    return render(request, 'contratos/lista.html', context)


# ── Detalhe do Contrato ───────────────────────────────────────────────────────
@login_required
def contrato_detalhe(request, pk):
    contrato = get_object_or_404(
        Contrato.objects.select_related('empresa', 'gestor_tecnico', 'gestor_admin'),
        pk=pk
    )
    hoje = date.today()

    # Escopo e aditivos
    itens    = contrato.itens.all()
    aditivos = contrato.aditivos.order_by('numero')

    # Valor total do escopo
    valor_escopo = sum(i.valor_total for i in itens)

    # Medições
    medicoes = contrato.medicoes.order_by('-competencia')
    total_medido = medicoes.filter(
        status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0
    total_pago = medicoes.filter(
        status='paga'
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0

    # Gastos
    gastos = contrato.gastos.filter(tipo='realizado')
    total_gastos = gastos.aggregate(t=Sum('valor'))['t'] or 0

    # Margem acumulada
    margem = total_medido - total_gastos
    margem_pct = round((margem / total_medido * 100), 1) if total_medido > 0 else 0

    # Quadro de mobilização
    cargos = contrato.cargos_obrigatorios.all()
    tem_deficit_critico = any(c.situacao == 'critico' for c in cargos)
    tem_deficit         = any(c.deficit > 0 for c in cargos)

    # Dias restantes
    dias_restantes = (contrato.data_termino_atual - hoje).days

    # Percentual do valor executado
    perc_exec = contrato.percentual_executado

    # Gráfico gastos por categoria
    gastos_categoria = {}
    for g in gastos:
        cat = g.get_categoria_display()
        gastos_categoria[cat] = gastos_categoria.get(cat, 0) + float(g.valor)

    context = {
        'contrato':          contrato,
        'itens':             itens,
        'aditivos':          aditivos,
        'valor_escopo':      valor_escopo,
        'medicoes':          medicoes[:10],
        'total_medido':      total_medido,
        'total_pago':        total_pago,
        'total_gastos':      total_gastos,
        'margem':            margem,
        'margem_pct':        margem_pct,
        'cargos':            cargos,
        'tem_deficit_critico': tem_deficit_critico,
        'tem_deficit':       tem_deficit,
        'dias_restantes':    dias_restantes,
        'perc_exec':         perc_exec,
        'hoje':              hoje,
        'chart_categorias':  json.dumps(list(gastos_categoria.keys())),
        'chart_valores':     json.dumps(list(gastos_categoria.values())),
    }
    return render(request, 'contratos/detalhe.html', context)


# ── Criar Contrato ────────────────────────────────────────────────────────────
@login_required
def contrato_criar(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.criado_por = request.user
            contrato.save()
            messages.success(request, f'Contrato {contrato.numero_sap} criado com sucesso!')
            return redirect('contratos:detalhe', pk=contrato.pk)
    else:
        form = ContratoForm()

    return render(request, 'contratos/form.html', {
        'form':  form,
        'titulo': 'Novo Contrato',
        'acao':   'Criar',
    })


# ── Editar Contrato ───────────────────────────────────────────────────────────
@login_required
def contrato_editar(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contrato {contrato.numero_sap} atualizado!')
            return redirect('contratos:detalhe', pk=contrato.pk)
    else:
        form = ContratoForm(instance=contrato)

    return render(request, 'contratos/form.html', {
        'form':     form,
        'contrato': contrato,
        'titulo':   f'Editar — {contrato.numero_sap}',
        'acao':     'Salvar',
    })


# ── Adicionar Item de Escopo ──────────────────────────────────────────────────
@login_required
def item_criar(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    if request.method == 'POST':
        form = ItemEscopoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.contrato = contrato
            item.save()
            messages.success(request, 'Item de escopo adicionado!')
            return redirect('contratos:detalhe', pk=contrato.pk)
    else:
        form = ItemEscopoForm()

    return render(request, 'contratos/form_item.html', {
        'form':     form,
        'contrato': contrato,
        'titulo':   'Novo Item de Escopo',
    })


# ── Adicionar Aditivo ─────────────────────────────────────────────────────────
@login_required
def aditivo_criar(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    if request.method == 'POST':
        form = AditivoForm(request.POST, request.FILES)
        if form.is_valid():
            aditivo = form.save(commit=False)
            aditivo.contrato = contrato

            # Atualiza o contrato conforme o tipo do aditivo
            if aditivo.tipo in ['valor', 'prazo_valor']:
                contrato.valor_atual += aditivo.valor_acrescimo
            if aditivo.tipo in ['prazo', 'prazo_valor'] and aditivo.nova_data_termino:
                contrato.data_termino_atual = aditivo.nova_data_termino
            contrato.save()

            aditivo.save()
            messages.success(
                request,
                f'{aditivo.numero}º Aditivo registrado! Contrato atualizado.'
            )
            return redirect('contratos:detalhe', pk=contrato.pk)
    else:
        # Sugere o próximo número de aditivo
        proximo = contrato.aditivos.count() + 1
        form = AditivoForm(initial={'numero': proximo})

    return render(request, 'contratos/form_aditivo.html', {
        'form':     form,
        'contrato': contrato,
        'titulo':   f'Novo Aditivo — {contrato.numero_sap}',
    })




@login_required
def exportar_contratos_pdf(request):
    qs = Contrato.objects.select_related('empresa').filter(status='vigente')
    buf  = pdf_contratos(list(qs))
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="Contratos_Vale.pdf"'
    return resp

@login_required
def exportar_contratos_excel(request):
    qs = Contrato.objects.select_related('empresa').filter(status='vigente')
    buf  = excel_contratos(list(qs))
    resp = HttpResponse(
        buf,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    resp['Content-Disposition'] = 'attachment; filename="Contratos_Vale.xlsx"'
    return resp



