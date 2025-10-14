"""
Página de Pagamentos - Gerenciamento de mensalidades
Integrado ao PagamentosService
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, List
from src.services.pagamentos_service import PagamentosService
from src.services.alunos_service import AlunosService

def show_pagamentos():
    """Exibe a página de gerenciamento de pagamentos"""
    
    # Inicializar serviços
    if 'pagamentos_service' not in st.session_state:
        try:
            st.session_state.pagamentos_service = PagamentosService()
        except Exception as e:
            st.error(f"❌ Erro ao conectar com pagamentos: {str(e)}")
            return
    
    if 'alunos_service' not in st.session_state:
        try:
            st.session_state.alunos_service = AlunosService()
        except Exception as e:
            st.error(f"❌ Erro ao conectar com alunos: {str(e)}")
            return
    
    pagamentos_service = st.session_state.pagamentos_service
    alunos_service = st.session_state.alunos_service
    
    st.markdown("## 💳 Gerenciamento de Pagamentos")
    
    # Controle de aba/modo
    if 'pagamentos_modo' not in st.session_state:
        st.session_state.pagamentos_modo = 'lista'
    
    # Menu de navegação
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("📋 Lista Pagamentos", use_container_width=True, 
                    type="primary" if st.session_state.pagamentos_modo == 'lista' else "secondary"):
            st.session_state.pagamentos_modo = 'lista'
            st.rerun()
    
    with col2:
        if st.button("➕ Registrar Pagamento", use_container_width=True,
                    type="primary" if st.session_state.pagamentos_modo == 'novo' else "secondary"):
            st.session_state.pagamentos_modo = 'novo'
            st.rerun()
    
    with col3:
        if st.button("🚫 Inadimplentes", use_container_width=True,
                    type="primary" if st.session_state.pagamentos_modo == 'inadimplentes' else "secondary"):
            st.session_state.pagamentos_modo = 'inadimplentes'
            st.rerun()
    
    with col4:
        if st.button("📊 Estatísticas", use_container_width=True,
                    type="primary" if st.session_state.pagamentos_modo == 'stats' else "secondary"):
            st.session_state.pagamentos_modo = 'stats'
            st.rerun()
    
    st.markdown("---")
    
    # Renderizar conteúdo baseado no modo
    if st.session_state.pagamentos_modo == 'lista':
        _mostrar_lista_pagamentos(pagamentos_service, alunos_service)
    elif st.session_state.pagamentos_modo == 'novo':
        _mostrar_formulario_novo_pagamento(pagamentos_service, alunos_service)
    elif st.session_state.pagamentos_modo == 'editar':
        _mostrar_formulario_editar_pagamento(pagamentos_service, alunos_service)
    elif st.session_state.pagamentos_modo == 'inadimplentes':
        _mostrar_inadimplentes(pagamentos_service)
    elif st.session_state.pagamentos_modo == 'stats':
        _mostrar_estatisticas_pagamentos(pagamentos_service)

def _mostrar_lista_pagamentos(pagamentos_service: PagamentosService, alunos_service: AlunosService):
    """Mostra busca de alunos e seus pagamentos em painéis expansíveis"""
    
    st.markdown("### � Buscar Pagamentos por Aluno")
    
    # Campo de busca por nome do aluno
    col1, col2 = st.columns([3, 1])
    
    with col1:
        termo_busca = st.text_input(
            "🔍 Digite o nome do aluno:",
            placeholder="Ex: João Silva, Maria...",
            help="Digite pelo menos 2 caracteres para buscar"
        )
    
    with col2:
        st.write("") # Spacer
        limpar_busca = st.button("🗑️ Limpar", use_container_width=True)
        if limpar_busca:
            st.rerun()
    
    # Se não há termo de busca, mostrar instruções
    if not termo_busca or len(termo_busca.strip()) < 2:
        st.info("ℹ️ Digite pelo menos 2 caracteres no campo de busca para encontrar alunos e ver seus pagamentos.")
        return
    
    # Buscar alunos que correspondem ao termo
    try:
        alunos_encontrados = alunos_service.buscar_alunos_por_nome(termo_busca.strip())
        
        if not alunos_encontrados:
            st.warning(f"❌ Nenhum aluno encontrado com o termo: '{termo_busca}'")
            return
            
        st.success(f"✅ {len(alunos_encontrados)} aluno(s) encontrado(s)")
        
        # Para cada aluno encontrado, mostrar seus pagamentos em painel expansível
        for aluno in alunos_encontrados:
            aluno_id = aluno.get('id')
            aluno_nome = aluno.get('nome', 'Nome não informado')
            aluno_status = aluno.get('status', 'indefinido')
            
            # Status do aluno com emoji
            status_emoji = "🟢" if aluno_status == "ativo" else "🔴"
            
            # Buscar pagamentos do aluno
            pagamentos_aluno = pagamentos_service.listar_pagamentos_por_aluno(aluno_id)
            total_pagamentos = len(pagamentos_aluno)
            
            # Calcular estatísticas rápidas
            pagos = sum(1 for p in pagamentos_aluno if p.get('status') == 'pago')
            inadimplentes = sum(1 for p in pagamentos_aluno if p.get('status') == 'inadimplente')
            
            # Painel expansível para cada aluno
            with st.expander(
                f"{status_emoji} {aluno_nome} - {total_pagamentos} pagamento(s) | ✅ {pagos} pago(s) | ❌ {inadimplentes} inadimplente(s)",
                expanded=len(alunos_encontrados) == 1  # Expande automaticamente se só há 1 aluno
            ):
                if not pagamentos_aluno:
                    st.info(f"📭 Nenhum pagamento encontrado para {aluno_nome}")
                    continue
                
                # Organizar pagamentos por ano/mês (mais recente primeiro)
                pagamentos_ordenados = sorted(
                    pagamentos_aluno, 
                    key=lambda x: x.get('ym', ''), 
                    reverse=True
                )
                
                # Mostrar pagamentos em formato compacto
                for pagamento in pagamentos_ordenados:
                    status = pagamento.get('status', 'indefinido')
                    ym = pagamento.get('ym', 'Data não informada')
                    valor = pagamento.get('valor', 0)
                    exigivel = pagamento.get('exigivel', False)
                    
                    # Definir cor e emoji por status
                    if status == 'pago':
                        cor = "🟢"
                        status_texto = "Pago"
                    elif status == 'inadimplente':
                        cor = "🔴"
                        status_texto = "Inadimplente"
                    elif status == 'ausente':
                        cor = "🟡"
                        status_texto = "Ausente"
                    else:
                        cor = "⚪"
                        status_texto = "Indefinido"
                    
                    exigivel_texto = "💰 Exigível" if exigivel else "🚫 Não exigível"
                    
                    # Layout compacto para cada pagamento
                    col_mes, col_status, col_valor, col_acoes = st.columns([2, 2, 2, 1])
                    
                    with col_mes:
                        st.write(f"📅 **{ym}**")
                    
                    with col_status:
                        st.write(f"{cor} **{status_texto}**")
                    
                    with col_valor:
                        st.write(f"💵 **R$ {valor:.2f}**")
                        st.caption(exigivel_texto)
                    
                    with col_acoes:
                        if st.button("✏️", key=f"edit_{pagamento.get('id')}", help="Editar pagamento"):
                            st.session_state.pagamento_editando = pagamento.get('id')
                            st.session_state.pagamentos_modo = 'editar'
                            st.rerun()
                    
                    st.divider()
    
    except Exception as e:
        st.error(f"❌ Erro ao buscar pagamentos: {str(e)}")

def _mostrar_formulario_editar_pagamento(pagamentos_service: PagamentosService, alunos_service: AlunosService):
    """Mostra formulário para editar pagamento existente"""
    
    if 'pagamento_editando' not in st.session_state:
        st.error("❌ Nenhum pagamento selecionado para edição")
        if st.button("🔙 Voltar à Lista"):
            st.session_state.pagamentos_modo = 'lista'
            st.rerun()
        return
    
    pagamento_id = st.session_state.pagamento_editando
    
    try:
        # Buscar pagamento atual
        pagamento = pagamentos_service.buscar_pagamento(pagamento_id)
        if not pagamento:
            st.error("❌ Pagamento não encontrado")
            if st.button("🔙 Voltar à Lista"):
                st.session_state.pagamentos_modo = 'lista'
                del st.session_state.pagamento_editando
                st.rerun()
            return
        
        st.markdown("### ✏️ Editar Pagamento")
        st.info(f"📝 Editando pagamento: **{pagamento.get('alunoNome', 'N/A')}** - {pagamento.get('ym', 'N/A')}")
        
        with st.form("form_editar_pagamento"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Status do pagamento
                status_atual = pagamento.get('status', 'ausente')
                novo_status = st.selectbox(
                    "📊 Status:",
                    options=['pago', 'inadimplente', 'ausente'],
                    index=['pago', 'inadimplente', 'ausente'].index(status_atual),
                    help="Status atual do pagamento"
                )
                
                # Valor
                valor_atual = pagamento.get('valor', 0.0)
                novo_valor = st.number_input(
                    "💰 Valor (R$):",
                    min_value=0.0,
                    value=float(valor_atual),
                    step=0.01,
                    format="%.2f"
                )
            
            with col2:
                # Data de vencimento
                vencimento_atual = pagamento.get('vencimento', '')
                try:
                    data_vencimento_atual = datetime.strptime(vencimento_atual, '%Y-%m-%d').date() if vencimento_atual else date.today()
                except:
                    data_vencimento_atual = date.today()
                
                nova_data_vencimento = st.date_input(
                    "📅 Data Vencimento:",
                    value=data_vencimento_atual
                )
                
                # Data de pagamento (se pago)
                data_pagamento_atual = pagamento.get('dataPagamento', '')
                if data_pagamento_atual:
                    try:
                        data_pag_inicial = datetime.strptime(data_pagamento_atual, '%Y-%m-%d').date()
                    except:
                        data_pag_inicial = None
                else:
                    data_pag_inicial = None
                
                nova_data_pagamento = st.date_input(
                    "💳 Data Pagamento:",
                    value=data_pag_inicial,
                    help="Data em que o pagamento foi realizado (opcional)"
                )
            
            # Observações
            obs_atual = pagamento.get('obs', '')
            novas_obs = st.text_area(
                "📝 Observações:",
                value=obs_atual,
                placeholder="Observações sobre o pagamento..."
            )
            
            # Botões
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                    try:
                        # Preparar dados de atualização
                        dados_atualizacao = {
                            'status': novo_status,
                            'valor': novo_valor,
                            'vencimento': nova_data_vencimento.strftime('%Y-%m-%d')
                        }
                        
                        # Adicionar data de pagamento se fornecida
                        if nova_data_pagamento:
                            dados_atualizacao['dataPagamento'] = nova_data_pagamento.strftime('%Y-%m-%d')
                        
                        # Adicionar observações se fornecidas
                        if novas_obs.strip():
                            dados_atualizacao['obs'] = novas_obs.strip()
                        
                        # Atualizar pagamento
                        sucesso = pagamentos_service.atualizar_pagamento(pagamento_id, dados_atualizacao)
                        
                        if sucesso:
                            st.success("✅ Pagamento atualizado com sucesso!")
                            # Voltar para lista após 2 segundos
                            st.session_state.pagamentos_modo = 'lista'
                            del st.session_state.pagamento_editando
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar pagamento")
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")
            
            with col2:
                if st.form_submit_button("🔙 Cancelar", use_container_width=True):
                    st.session_state.pagamentos_modo = 'lista'
                    del st.session_state.pagamento_editando
                    st.rerun()
            
            with col3:
                if st.form_submit_button("🗑️ Excluir", use_container_width=True):
                    # Confirmar exclusão em modal (simplificado)
                    st.session_state.confirmar_exclusao = pagamento_id
                    st.rerun()
        
        # Modal de confirmação de exclusão
        if st.session_state.get('confirmar_exclusao') == pagamento_id:
            st.error("⚠️ **Confirmar Exclusão**")
            st.warning(f"Tem certeza que deseja excluir o pagamento de **{pagamento.get('alunoNome', 'N/A')}**?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sim, Excluir", type="primary", use_container_width=True):
                    try:
                        sucesso = pagamentos_service.deletar_pagamento(pagamento_id)
                        if sucesso:
                            st.success("✅ Pagamento excluído com sucesso!")
                            st.session_state.pagamentos_modo = 'lista'
                            del st.session_state.pagamento_editando
                            del st.session_state.confirmar_exclusao
                            st.rerun()
                        else:
                            st.error("❌ Erro ao excluir pagamento")
                    except Exception as e:
                        st.error(f"❌ Erro ao excluir: {str(e)}")
            
            with col2:
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state.confirmar_exclusao
                    st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar pagamento: {str(e)}")
        if st.button("🔙 Voltar à Lista"):
            st.session_state.pagamentos_modo = 'lista'
            if 'pagamento_editando' in st.session_state:
                del st.session_state.pagamento_editando
            st.rerun()

def _mostrar_formulario_novo_pagamento(pagamentos_service: PagamentosService, alunos_service: AlunosService):
    """Mostra formulário para registrar novo pagamento"""
    
    st.markdown("### ➕ Registrar Novo Pagamento")
    
    # Mostrar sucesso se pagamento foi registrado
    if 'pagamento_registrado' in st.session_state:
        pagamento_info = st.session_state.pagamento_registrado
        st.success(f"✅ Pagamento de **{pagamento_info['aluno_nome']}** registrado!")
        st.info(f"💰 Valor: R$ {pagamento_info['valor']:.2f}")
        st.info(f"📅 Referente a: {pagamento_info['ym']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Ver Lista", type="primary", use_container_width=True):
                del st.session_state.pagamento_registrado
                st.session_state.pagamentos_modo = 'lista'
                st.rerun()
        
        with col2:
            if st.button("➕ Registrar Outro", type="secondary", use_container_width=True):
                del st.session_state.pagamento_registrado
                st.rerun()
        
        st.markdown("---")
    
    with st.form("form_novo_pagamento", clear_on_submit=True):
        # Dados básicos
        st.markdown("#### � Dados do Pagamento")
        
        # Carregar alunos ativos para seleção
        try:
            alunos_ativos = alunos_service.listar_alunos(status='ativo')
            alunos_opcoes = {f"{aluno['nome']} (ID: {aluno['id']})": aluno['id'] 
                           for aluno in alunos_ativos}
            
            if not alunos_opcoes:
                st.error("❌ Nenhum aluno ativo encontrado! Cadastre alunos primeiro.")
                return
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar alunos: {str(e)}")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            aluno_selecionado = st.selectbox(
                "� Aluno *",
                options=list(alunos_opcoes.keys()),
                help="Selecione o aluno para registrar o pagamento"
            )
            
            hoje = date.today()
            mes_ref = st.number_input("📅 Mês de Referência *", min_value=1, max_value=12, value=hoje.month)
            ano_ref = st.number_input("📅 Ano de Referência *", min_value=2020, max_value=2030, value=hoje.year)
        
        with col2:
            valor = st.number_input("💰 Valor (R$) *", min_value=0.01, step=0.01, format="%.2f", value=150.0)
            
            status = st.selectbox(
                "📊 Status *",
                options=["pago", "inadimplente", "ausente"],
                index=0,
                help="Status do pagamento"
            )
        
        # Opções adicionais
        st.markdown("#### ⚙️ Opções")
        exigivel = st.checkbox("💳 Exigível (conta para cobrança)", value=True, 
                              help="Se desmarcado, não será considerado para cálculo de inadimplência")
        
        # Observações
        observacoes = st.text_area("📝 Observações", placeholder="Observações sobre o pagamento (opcional)")
        
        # Botões
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submitted = st.form_submit_button("✅ Registrar", type="primary", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🔄 Limpar", use_container_width=True):
                st.rerun()
        
        # Processar formulário
        if submitted:
            # Validações
            if not aluno_selecionado:
                st.error("❌ Selecione um aluno!")
                return
            
            if valor <= 0:
                st.error("❌ Valor deve ser maior que zero!")
                return
            
            # Obter dados do aluno
            aluno_id = alunos_opcoes[aluno_selecionado]
            
            # Buscar dados completos do aluno
            try:
                aluno = alunos_service.buscar_aluno(aluno_id)
                if not aluno:
                    st.error("❌ Aluno não encontrado!")
                    return
                
                aluno_nome = aluno.get('nome', 'N/A')
                
            except Exception as e:
                st.error(f"❌ Erro ao buscar aluno: {str(e)}")
                return
            
            # Verificar se já existe pagamento para este aluno/mês
            try:
                pagamento_existente = pagamentos_service.buscar_pagamento_por_aluno_mes(
                    aluno_id, ano_ref, mes_ref
                )
                
                if pagamento_existente:
                    st.warning(f"⚠️ Já existe pagamento para este aluno em {mes_ref:02d}/{ano_ref}")
                    return
                
            except Exception as e:
                st.error(f"❌ Erro ao verificar pagamento existente: {str(e)}")
                return
            
            # Preparar dados do pagamento
            dados_pagamento = {
                'alunoId': aluno_id,
                'alunoNome': aluno_nome,
                'ano': ano_ref,
                'mes': mes_ref,
                'valor': valor,
                'status': status,
                'exigivel': exigivel
            }
            
            if observacoes.strip():
                dados_pagamento['observacoes'] = observacoes.strip()
            
            # Registrar pagamento
            try:
                pagamento_id = pagamentos_service.criar_pagamento(dados_pagamento)
                st.session_state.pagamento_registrado = {
                    'id': pagamento_id,
                    'aluno_nome': aluno_nome,
                    'valor': valor,
                    'ym': f"{ano_ref:04d}-{mes_ref:02d}"
                }
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao registrar pagamento: {str(e)}")

def _mostrar_inadimplentes(pagamentos_service: PagamentosService):
    """Mostra lista de inadimplentes"""
    
    st.markdown("### 🚫 Lista de Inadimplentes")
    
    # Filtro de mês
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Gerar opções de mês/ano
        hoje = date.today()
        meses_opcoes = ["Todos os meses"]
        for i in range(6):  # Últimos 6 meses
            if i == 0:
                mes_ano = f"{hoje.year:04d}-{hoje.month:02d}"
            else:
                mes = hoje.month - i
                ano = hoje.year
                if mes <= 0:
                    mes += 12
                    ano -= 1
                mes_ano = f"{ano:04d}-{mes:02d}"
            meses_opcoes.append(mes_ano)
        
        mes_filtro = st.selectbox("📅 Filtrar por mês:", options=meses_opcoes, index=1)
    
    # Carregar inadimplentes
    try:
        if mes_filtro == "Todos os meses":
            inadimplentes = pagamentos_service.obter_inadimplentes()
        else:
            inadimplentes = pagamentos_service.obter_inadimplentes(ym=mes_filtro)
        
        if not inadimplentes:
            st.success("🎉 Nenhum inadimplente encontrado! Parabéns!")
            return
        
        # Exibir inadimplentes
        st.error(f"⚠️ **{len(inadimplentes)} inadimplente(s) encontrado(s)**")
        
        for pagamento in inadimplentes:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**🔴 {pagamento.get('alunoNome', 'N/A')}**")
                    st.markdown(f"📅 Referente a: {pagamento.get('ym', 'N/A')}")
                
                with col2:
                    st.markdown(f"💰 Valor: R$ {pagamento.get('valor', 0):.2f}")
                    
                    # Calcular dias em atraso (estimativa)
                    try:
                        ano, mes = map(int, pagamento.get('ym', '2024-01').split('-'))
                        data_vencimento = date(ano, mes, 15)  # Assumindo vencimento dia 15
                        dias_atraso = (date.today() - data_vencimento).days
                        
                        if dias_atraso > 0:
                            st.markdown(f"⏰ {dias_atraso} dias em atraso")
                        else:
                            st.markdown(f"⏰ Vence em {abs(dias_atraso)} dias")
                    except:
                        st.markdown("⏰ Calcular atraso")
                
                with col3:
                    if st.button("💰 Pagar", key=f"pagar_inadim_{pagamento.get('id')}", use_container_width=True):
                        if pagamentos_service.marcar_como_pago(pagamento.get('id')):
                            st.success("Pagamento registrado!")
                            st.rerun()
                
                st.markdown("---")
        
        # Resumo financeiro
        valor_total_inadimplencia = sum(p.get('valor', 0) for p in inadimplentes)
        st.error(f"💸 **Total inadimplente: R$ {valor_total_inadimplencia:.2f}**")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar inadimplentes: {str(e)}")

def _mostrar_estatisticas_pagamentos(pagamentos_service: PagamentosService):
    """Mostra estatísticas de pagamentos"""
    
    st.markdown("### 📊 Estatísticas de Pagamentos")
    
    # Seletor de mês
    col1, col2 = st.columns([1, 3])
    
    with col1:
        hoje = date.today()
        mes_atual = f"{hoje.year:04d}-{hoje.month:02d}"
        
        # Gerar opções de mês
        meses_opcoes = []
        for i in range(12):
            mes = hoje.month - i
            ano = hoje.year
            if mes <= 0:
                mes += 12
                ano -= 1
            mes_ano = f"{ano:04d}-{mes:02d}"
            meses_opcoes.append(mes_ano)
        
        ym_stats = st.selectbox("📅 Mês para análise:", options=meses_opcoes, index=0)
    
    # Obter estatísticas
    try:
        stats = pagamentos_service.obter_estatisticas_mes(ym_stats)
        
        # Exibir métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Receita Total",
                value=f"R$ {stats['receita_total']:.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="✅ Pagamentos Confirmados",
                value=stats['total_pagos'],
                delta=f"{stats['total_pagos']}/{stats['total_pagamentos']}"
            )
        
        with col3:
            st.metric(
                label="🚫 Inadimplentes",
                value=stats['total_inadimplentes'],
                delta=f"R$ {stats['valor_inadimplencia']:.2f}"
            )
        
        with col4:
            st.metric(
                label="📊 Taxa Inadimplência",
                value=f"{stats['taxa_inadimplencia']:.1f}%",
                delta=None
            )
        
        # Gráficos e detalhes
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Distribuição por Status")
            
            # Criar DataFrame para gráfico
            chart_data = pd.DataFrame({
                'Status': ['Pagos', 'Inadimplentes', 'Ausentes'],
                'Quantidade': [stats['total_pagos'], stats['total_inadimplentes'], stats['total_ausentes']],
                'Valor': [stats['receita_total'], stats['valor_inadimplencia'], 0]
            })
            
            st.bar_chart(chart_data.set_index('Status')['Quantidade'])
        
        with col2:
            st.markdown("#### 💵 Valores por Status")
            st.bar_chart(chart_data.set_index('Status')['Valor'])
        
        # Lista detalhada
        if st.checkbox("📋 Mostrar detalhes dos pagamentos"):
            st.markdown("#### 📋 Detalhes dos Pagamentos")
            
            tab1, tab2, tab3 = st.tabs(["✅ Pagos", "🚫 Inadimplentes", "⚪ Ausentes"])
            
            with tab1:
                pagos = stats['detalhes']['pagos']
                if pagos:
                    for p in pagos:
                        st.write(f"✅ {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f}")
                else:
                    st.info("Nenhum pagamento confirmado")
            
            with tab2:
                inadimplentes = stats['detalhes']['inadimplentes']
                if inadimplentes:
                    for p in inadimplentes:
                        st.write(f"🚫 {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f}")
                else:
                    st.success("Nenhum inadimplente! 🎉")
            
            with tab3:
                ausentes = stats['detalhes']['ausentes']
                if ausentes:
                    for p in ausentes:
                        st.write(f"⚪ {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f}")
                else:
                    st.info("Nenhum ausente registrado")
        
    except Exception as e:
        st.error(f"❌ Erro ao obter estatísticas: {str(e)}")

def show_presencas():
    """Página de Presenças - Sprint 3"""
    st.markdown("## ✅ Presenças")
    st.info("🚧 **Sprint 3** - Implementação prevista")
    st.markdown("- Check-in de alunos\n- Relatório mensal\n- Histórico de presenças")

def show_graduacoes():
    """Página de Graduações - Sprint 3"""
    st.markdown("## 🥋 Graduações")
    st.info("🚧 **Sprint 3** - Implementação prevista")
    st.markdown("- Registro de promoções\n- Timeline por aluno\n- Histórico de graduações")

def show_planos():
    """Página de Planos - Sprint 1"""
    st.markdown("## 📋 Planos")
    st.info("🚧 **Sprint 1** - Implementação prevista")
    st.markdown("- CRUD de planos\n- Apenas planos mensais no MVP\n- Configuração de valores")