from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from datetime import date, timedelta
from .models import Medicao, GastoOperacional
from .forms import MedicaoForm, GastoForm
from contratos.models import Contrato
import json


# ── DRE Mensal de um contrato ─────────────────────────────────────────────────
@login_required
def dre_contrato(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    hoje     = date.today()

    # Meses disponíveis (todos os meses com medição ou gasto)
    meses_medicao = Medicao.objects.filter(
        contrato=contrato
    ).dates('competencia', 'month', order='DESC')

    meses_gasto = GastoOperacional.objects.filter(
        contrato=contrato
    ).dates('competencia', 'month', order='DESC')

    # Une e ordena os meses
    todos_meses = sorted(
        set(list(meses_medicao) + list(meses_gasto)),
        reverse=True
    )

    # Mês selecionado pelo filtro
    mes_param = request.GET.get('mes', '')
    if mes_param:
        try:
            from datetime import datetime
            mes_sel = datetime.strptime(mes_param, '%Y-%m').date()
        except ValueError:
            mes_sel = hoje.replace(day=1)
    else:
        mes_sel = hoje.replace(day=1)

    # Medições do mês selecionado
    medicoes = Medicao.objects.filter(
        contrato=contrato,
        competencia=mes_sel
    ).order_by('numero')

    fat_bruto   = medicoes.aggregate(t=Sum('valor_bruto'))['t'] or 0
    fat_glosa   = medicoes.aggregate(t=Sum('valor_glosa'))['t'] or 0
    fat_retencao = medicoes.aggregate(t=Sum('valor_retencao'))['t'] or 0
    fat_liquido  = fat_bruto - fat_glosa - fat_retencao

    # Gastos do mês por categoria
    gastos_qs = GastoOperacional.objects.filter(
        contrato=contrato,
        competencia=mes_sel,
        tipo='realizado'
    )

    gastos_por_categoria = {}
    for cat_key, cat_label in GastoOperacional.CATEGORIAS:
        total = gastos_qs.filter(
            categoria=cat_key
        ).aggregate(t=Sum('valor'))['t'] or 0
        if total > 0:
            gastos_por_categoria[cat_label] = total

    total_gastos = gastos_qs.aggregate(t=Sum('valor'))['t'] or 0
    margem       = fat_liquido - total_gastos
    margem_pct   = round((margem / fat_liquido * 100), 1) if fat_liquido > 0 else 0

    # Acumulado total do contrato
    fat_acumulado = Medicao.objects.filter(
        contrato=contrato,
        status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0

    gastos_acumulado = GastoOperacional.objects.filter(
        contrato=contrato, tipo='realizado'
    ).aggregate(t=Sum('valor'))['t'] or 0

    margem_acumulada     = fat_acumulado - gastos_acumulado
    margem_acumulada_pct = round(
        (margem_acumulada / fat_acumulado * 100), 1
    ) if fat_acumulado > 0 else 0

    # Gráfico dos últimos 6 meses
    labels, fat_data, gasto_data, margem_data = [], [], [], []
    for i in range(5, -1, -1):
        d = (hoje.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        f = Medicao.objects.filter(
            contrato=contrato, competencia=d,
            status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
        ).aggregate(t=Sum('valor_bruto'))['t'] or 0
        g = GastoOperacional.objects.filter(
            contrato=contrato, competencia=d, tipo='realizado'
        ).aggregate(t=Sum('valor'))['t'] or 0
        labels.append(d.strftime('%b/%y'))
        fat_data.append(float(f))
        gasto_data.append(float(g))
        margem_data.append(float(f - g))

    context = {
        'contrato':            contrato,
        'todos_meses':         todos_meses,
        'mes_sel':             mes_sel,
        'mes_param':           mes_sel.strftime('%Y-%m'),
        # Faturamento
        'medicoes':            medicoes,
        'fat_bruto':           fat_bruto,
        'fat_glosa':           fat_glosa,
        'fat_retencao':        fat_retencao,
        'fat_liquido':         fat_liquido,
        # Gastos
        'gastos_por_categoria': gastos_por_categoria,
        'total_gastos':        total_gastos,
        # DRE do mês
        'margem':              margem,
        'margem_pct':          margem_pct,
        # Acumulado
        'fat_acumulado':       fat_acumulado,
        'gastos_acumulado':    gastos_acumulado,
        'margem_acumulada':    margem_acumulada,
        'margem_acumulada_pct': margem_acumulada_pct,
        # Gráfico
        'chart_labels':        json.dumps(labels),
        'chart_fat':           json.dumps(fat_data),
        'chart_gastos':        json.dumps(gasto_data),
        'chart_margem':        json.dumps(margem_data),
        # Gráfico pizza categorias
        'chart_cat_labels':    json.dumps(list(gastos_por_categoria.keys())),
        'chart_cat_valores':   json.dumps(
            [float(v) for v in gastos_por_categoria.values()]
        ),
    }
    return render(request, 'financeiro/dre.html', context)


# ── Medições ──────────────────────────────────────────────────────────────────
@login_required
def medicao_criar(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)

    # Verifica déficit crítico de quadro
    tem_deficit_critico = any(
        c.situacao == 'critico'
        for c in contrato.cargos_obrigatorios.all()
    )

    if request.method == 'POST':
        form = MedicaoForm(request.POST, request.FILES)
        if form.is_valid():
            medicao          = form.save(commit=False)
            medicao.contrato = contrato
            medicao.save()
            messages.success(
                request,
                f'BM-{medicao.numero:03d} registrado com sucesso!'
            )
            return redirect('financeiro:dre', contrato_pk=contrato.pk)
    else:
        # Sugere próximo número de BM
        proximo = contrato.medicoes.count() + 1
        form    = MedicaoForm(initial={
            'numero':     proximo,
            'competencia': date.today().replace(day=1),
        })

    return render(request, 'financeiro/form_medicao.html', {
        'form':                form,
        'contrato':            contrato,
        'titulo':              f'Nova Medição — {contrato.numero_sap}',
        'tem_deficit_critico': tem_deficit_critico,
    })


@login_required
def medicao_editar(request, pk):
    medicao  = get_object_or_404(Medicao, pk=pk)
    contrato = medicao.contrato
    if request.method == 'POST':
        form = MedicaoForm(request.POST, request.FILES, instance=medicao)
        if form.is_valid():
            form.save()
            messages.success(request, f'BM-{medicao.numero:03d} atualizado!')
            return redirect('financeiro:dre', contrato_pk=contrato.pk)
    else:
        form = MedicaoForm(instance=medicao)

    return render(request, 'financeiro/form_medicao.html', {
        'form':     form,
        'contrato': contrato,
        'medicao':  medicao,
        'titulo':   f'Editar BM-{medicao.numero:03d}',
    })


# ── Gastos Operacionais ───────────────────────────────────────────────────────
@login_required
def gasto_criar(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, request.FILES)
        if form.is_valid():
            gasto            = form.save(commit=False)
            gasto.contrato   = contrato
            gasto.lancado_por = request.user
            gasto.save()
            messages.success(
                request,
                f'Gasto de R$ {gasto.valor} registrado em {gasto.get_categoria_display()}!'
            )
            return redirect('financeiro:dre', contrato_pk=contrato.pk)
    else:
        form = GastoForm(initial={
            'competencia':    date.today().replace(day=1),
            'data_lancamento': date.today(),
        })

    return render(request, 'financeiro/form_gasto.html', {
        'form':     form,
        'contrato': contrato,
        'titulo':   f'Lançar Gasto — {contrato.numero_sap}',
    })


@login_required
def gasto_editar(request, pk):
    gasto    = get_object_or_404(GastoOperacional, pk=pk)
    contrato = gasto.contrato
    if request.method == 'POST':
        form = GastoForm(request.POST, request.FILES, instance=gasto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto atualizado!')
            return redirect('financeiro:dre', contrato_pk=contrato.pk)
    else:
        form = GastoForm(instance=gasto)

    return render(request, 'financeiro/form_gasto.html', {
        'form':     form,
        'contrato': contrato,
        'gasto':    gasto,
        'titulo':   f'Editar Gasto — {contrato.numero_sap}',
    })


# ── Lista de gastos do contrato ───────────────────────────────────────────────
@login_required
def gastos_lista(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    qs       = GastoOperacional.objects.filter(
        contrato=contrato
    ).order_by('-competencia', '-data_lancamento')

    # Filtros
    categoria = request.GET.get('categoria', '')
    mes       = request.GET.get('mes', '')

    if categoria:
        qs = qs.filter(categoria=categoria)
    if mes:
        try:
            from datetime import datetime
            mes_date = datetime.strptime(mes, '%Y-%m').date()
            qs = qs.filter(competencia=mes_date)
        except ValueError:
            pass

    total = qs.aggregate(t=Sum('valor'))['t'] or 0

    context = {
        'contrato':          contrato,
        'gastos':            qs,
        'total':             total,
        'categoria_atual':   categoria,
        'mes_atual':         mes,
        'categoria_choices': GastoOperacional.CATEGORIAS,
    }
    return render(request, 'financeiro/gastos_lista.html', context)

from utils.exportar import pdf_dre, excel_dre

@login_required
def exportar_dre_pdf(request, contrato_pk):
    from django.db.models import Sum
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    hoje     = date.today()

    mes_param = request.GET.get('mes', '')
    try:
        from datetime import datetime
        mes_sel = datetime.strptime(mes_param, '%Y-%m').date()
    except (ValueError, TypeError):
        mes_sel = hoje.replace(day=1)

    medicoes = Medicao.objects.filter(
        contrato=contrato, competencia=mes_sel
    ).order_by('numero')

    fat_bruto    = medicoes.aggregate(t=Sum('valor_bruto'))['t'] or 0
    fat_glosa    = medicoes.aggregate(t=Sum('valor_glosa'))['t'] or 0
    fat_retencao = medicoes.aggregate(t=Sum('valor_retencao'))['t'] or 0
    fat_liquido  = fat_bruto - fat_glosa - fat_retencao

    gastos_qs = GastoOperacional.objects.filter(
        contrato=contrato, competencia=mes_sel, tipo='realizado'
    )
    gastos_por_categoria = {}
    for cat_key, cat_label in GastoOperacional.CATEGORIAS:
        total = gastos_qs.filter(
            categoria=cat_key
        ).aggregate(t=Sum('valor'))['t'] or 0
        if total > 0:
            gastos_por_categoria[cat_label] = total

    total_gastos = gastos_qs.aggregate(t=Sum('valor'))['t'] or 0
    margem       = fat_liquido - total_gastos
    margem_pct   = round((margem / fat_liquido * 100), 1) if fat_liquido > 0 else 0

    fat_acumulado = Medicao.objects.filter(
        contrato=contrato,
        status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0

    gastos_acumulado = GastoOperacional.objects.filter(
        contrato=contrato, tipo='realizado'
    ).aggregate(t=Sum('valor'))['t'] or 0

    margem_acumulada     = fat_acumulado - gastos_acumulado
    margem_acumulada_pct = round(
        (margem_acumulada / fat_acumulado * 100), 1
    ) if fat_acumulado > 0 else 0

    return pdf_dre_contrato(
        contrato, mes_sel, medicoes,
        fat_bruto, fat_glosa, fat_retencao, fat_liquido,
        gastos_por_categoria, total_gastos, margem, margem_pct,
        fat_acumulado, gastos_acumulado,
        margem_acumulada, margem_acumulada_pct
    )


@login_required
def exportar_dre_excel(request, contrato_pk):
    from django.db.models import Sum
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    hoje     = date.today()

    mes_param = request.GET.get('mes', '')
    try:
        from datetime import datetime
        mes_sel = datetime.strptime(mes_param, '%Y-%m').date()
    except (ValueError, TypeError):
        mes_sel = hoje.replace(day=1)

    medicoes = Medicao.objects.filter(
        contrato=contrato, competencia=mes_sel
    ).order_by('numero')

    fat_bruto    = medicoes.aggregate(t=Sum('valor_bruto'))['t'] or 0
    fat_glosa    = medicoes.aggregate(t=Sum('valor_glosa'))['t'] or 0
    fat_retencao = medicoes.aggregate(t=Sum('valor_retencao'))['t'] or 0
    fat_liquido  = fat_bruto - fat_glosa - fat_retencao

    gastos_qs = GastoOperacional.objects.filter(
        contrato=contrato, competencia=mes_sel, tipo='realizado'
    )
    gastos_por_categoria = {}
    for cat_key, cat_label in GastoOperacional.CATEGORIAS:
        total = gastos_qs.filter(
            categoria=cat_key
        ).aggregate(t=Sum('valor'))['t'] or 0
        if total > 0:
            gastos_por_categoria[cat_label] = total

    total_gastos = gastos_qs.aggregate(t=Sum('valor'))['t'] or 0
    margem       = fat_liquido - total_gastos
    margem_pct   = round((margem / fat_liquido * 100), 1) if fat_liquido > 0 else 0

    fat_acumulado = Medicao.objects.filter(
        contrato=contrato,
        status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0

    gastos_acumulado = GastoOperacional.objects.filter(
        contrato=contrato, tipo='realizado'
    ).aggregate(t=Sum('valor'))['t'] or 0

    margem_acumulada     = fat_acumulado - gastos_acumulado
    margem_acumulada_pct = round(
        (margem_acumulada / fat_acumulado * 100), 1
    ) if fat_acumulado > 0 else 0

    return excel_dre_contrato(
        contrato, mes_sel, medicoes, gastos_por_categoria,
        fat_bruto, fat_glosa, fat_retencao, fat_liquido,
        total_gastos, margem, margem_pct,
        fat_acumulado, gastos_acumulado,
        margem_acumulada, margem_acumulada_pct
    )