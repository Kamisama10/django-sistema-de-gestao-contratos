from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Empresa
from .forms import EmpresaForm
from contratos.models import Contrato
from financeiro.models import Medicao


@login_required
def empresa_lista(request):
    qs    = Empresa.objects.all()
    busca = request.GET.get('q', '')
    area  = request.GET.get('area', '')
    ativa = request.GET.get('ativa', '')

    if busca:
        qs = qs.filter(
            Q(razao_social__icontains=busca) |
            Q(cnpj__icontains=busca) |
            Q(nome_fantasia__icontains=busca)
        )
    if area:
        qs = qs.filter(area_atuacao=area)
    if ativa != '':
        qs = qs.filter(ativa=(ativa == '1'))

    # Anota cada empresa com total de contratos
    qs = qs.annotate(total_contratos=Count('contratos'))

    context = {
        'empresas':      qs,
        'total':         qs.count(),
        'busca':         busca,
        'area_atual':    area,
        'ativa_atual':   ativa,
        'area_choices':  Empresa.AREAS,
    }
    return render(request, 'empresas/lista.html', context)


@login_required
def empresa_detalhe(request, pk):
    empresa   = get_object_or_404(Empresa, pk=pk)
    contratos = Contrato.objects.filter(
        empresa=empresa
    ).order_by('-criado_em')

    # Totais por status
    vigentes   = contratos.filter(status='vigente').count()
    encerrados = contratos.filter(status='encerrado').count()

    # Valor total da carteira com essa empresa
    valor_carteira = contratos.filter(
        status='vigente'
    ).aggregate(t=Sum('valor_atual'))['t'] or 0

    # Total já faturado por essa empresa
    total_faturado = Medicao.objects.filter(
        contrato__empresa=empresa,
        status__in=['aprovada', 'glosada', 'nf_emitida', 'paga']
    ).aggregate(t=Sum('valor_bruto'))['t'] or 0

    context = {
        'empresa':        empresa,
        'contratos':      contratos,
        'vigentes':       vigentes,
        'encerrados':     encerrados,
        'valor_carteira': valor_carteira,
        'total_faturado': total_faturado,
    }
    return render(request, 'empresas/detalhe.html', context)


@login_required
def empresa_criar(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            messages.success(request, f'Empresa {empresa.razao_social} cadastrada!')
            return redirect('empresas:detalhe', pk=empresa.pk)
    else:
        form = EmpresaForm()

    return render(request, 'empresas/form.html', {
        'form':   form,
        'titulo': 'Nova Empresa',
        'acao':   'Cadastrar',
    })


@login_required
def empresa_editar(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Empresa {empresa.razao_social} atualizada!')
            return redirect('empresas:detalhe', pk=empresa.pk)
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, 'empresas/form.html', {
        'form':     form,
        'empresa':  empresa,
        'titulo':   f'Editar — {empresa.razao_social}',
        'acao':     'Salvar',
    })
