"""
Página de Pagamentos - Gerenciamento de mensalidades
Integrado ao PagamentosService
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
from src.services.pagamentos_service import PagamentosService
from src.services.alunos_service import AlunosService
from src.utils.cache_service import get_cache_manager

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
    
    # Editar é um overlay que substitui as tabs
    if st.session_state.pagamentos_modo == 'editar':
        _mostrar_formulario_editar_pagamento(pagamentos_service, alunos_service)
        return
    
    # Navegação por tabs (sem rerun ao trocar de aba)
    tab_cobrar, tab_inadim = st.tabs(
        ["🔔 A Cobrar", "🔴 Inadimplentes"]
    )
    
    with tab_cobrar:
        _mostrar_devedores(pagamentos_service)
    with tab_inadim:
        _mostrar_inadimplentes(pagamentos_service)

def _mostrar_lista_pagamentos_filtrada(pagamentos_service: PagamentosService, alunos_service: AlunosService):
    """Mostra lista unificada de pagamentos com filtros por turma e status"""
    
    st.markdown("### 📋 Lista de Pagamentos")
    
    # Área de filtros
    col_filtro1, col_filtro2, col_filtro3, col_busca = st.columns([2, 2, 2, 3])
    
    with col_filtro1:
        # Filtro por Status
        status_opcoes = {
            "Todos": None,
            "🟢 Pagos": "pago",
            "🔔 A Cobrar": "devedor",
            "🔴 Inadimplentes": "inadimplente",
            "⚪ Ausentes": "ausente"
        }
        status_selecionado = st.selectbox(
            "📊 Status:",
            options=list(status_opcoes.keys()),
            index=0,
            key="pag_filtro_status"
        )
        filtro_status = status_opcoes[status_selecionado]
    
    with col_filtro2:
        # Filtro por Turma
        try:
            from src.services.turmas_service import TurmasService
            turmas_service = TurmasService()
            turmas = turmas_service.listar_turmas()
            turmas_opcoes = {"Todas as turmas": None}
            turmas_opcoes.update({f"{t.get('nome', 'Sem nome')}": t.get('id') for t in turmas})
            
            turma_selecionada = st.selectbox(
                "🥋 Turma:",
                options=list(turmas_opcoes.keys()),
                index=0,
                key="pag_filtro_turma"
            )
            filtro_turma = turmas_opcoes[turma_selecionada]
        except:
            filtro_turma = None
            st.caption("⚠️ Turmas indisponíveis")
    
    with col_filtro3:
        # Filtro por Mês
        hoje = date.today()
        modo = st.session_state.get('data_mode', 'operacional')
        min_ym = "2026-01" if modo == 'operacional' else "2024-01"
        meses_opcoes = ["Todos os meses"]
        for i in range(12):
            if i == 0:
                mes_ano = f"{hoje.year:04d}-{hoje.month:02d}"
            else:
                mes = hoje.month - i
                ano = hoje.year
                if mes <= 0:
                    mes += 12
                    ano -= 1
                mes_ano = f"{ano:04d}-{mes:02d}"

            if mes_ano < min_ym:
                continue

            meses_opcoes.append(mes_ano)
        
        mes_selecionado = st.selectbox("📅 Mês:", options=meses_opcoes, index=1 if len(meses_opcoes) > 1 else 0, key="pag_filtro_mes")
        filtro_mes = None if mes_selecionado == "Todos os meses" else mes_selecionado
    
    with col_busca:
        # Busca por nome
        termo_busca = st.text_input(
            "🔍 Buscar aluno:",
            placeholder="Digite o nome...",
            help="Busque por nome do aluno",
            key="pag_busca_todos"
        )
    
    # Botão de limpar filtros
    if st.button("Limpar Filtros", key="pag_limpar_filtros"):
        st.rerun()
    
    st.markdown("---")
    
    # Aplicar filtros e buscar pagamentos
    try:
        # Se tem termo de busca, buscar alunos primeiro
        if termo_busca and len(termo_busca.strip()) >= 2:
            alunos_encontrados = alunos_service.buscar_alunos_por_nome(termo_busca.strip())
            
            if not alunos_encontrados:
                st.warning(f"❌ Nenhum aluno encontrado com o termo: '{termo_busca}'")
                return
            
            # IDs dos alunos encontrados
            alunos_ids = [a.get('id') for a in alunos_encontrados]
        else:
            alunos_ids = None
        
        # Buscar pagamentos baseado nos filtros
        if filtro_mes:
            # Se tem filtro de mês, buscar por mês
            pagamentos = pagamentos_service.listar_pagamentos(filtros={'ym': filtro_mes})
        else:
            # Buscar todos (limitado)
            pagamentos = pagamentos_service.listar_pagamentos()
        
        # Pré-carregar mapa alunoId → turmaId (evita N queries individuais)
        aluno_turma_map = {}
        if filtro_turma:
            cache_manager = get_cache_manager()
            todos_alunos = cache_manager.get_alunos_cached(alunos_service)
            aluno_turma_map = {a['id']: a.get('turmaId') for a in todos_alunos}
        
        # Aplicar filtros no cliente
        pagamentos_filtrados = []
        for pag in pagamentos:
            # Filtro de status
            if filtro_status and pag.get('status') != filtro_status:
                continue
            
            # Filtro de aluno (se tem busca)
            if alunos_ids and pag.get('alunoId') not in alunos_ids:
                continue
            
            # Filtro de turma (usa mapa pré-carregado)
            if filtro_turma:
                if aluno_turma_map.get(pag.get('alunoId')) != filtro_turma:
                    continue
            
            pagamentos_filtrados.append(pag)
        
        # Mostrar resultados
        if not pagamentos_filtrados:
            st.info("📭 Nenhum pagamento encontrado com os filtros aplicados.")
            return
        
        # Estatísticas rápidas
        total = len(pagamentos_filtrados)
        pagos = sum(1 for p in pagamentos_filtrados if p.get('status') == 'pago')
        devedores = sum(1 for p in pagamentos_filtrados if p.get('status') == 'devedor')
        inadimplentes = sum(1 for p in pagamentos_filtrados if p.get('status') == 'inadimplente')
        valor_total = sum(p.get('valor', 0) for p in pagamentos_filtrados if p.get('status') in ['devedor', 'inadimplente'])
        
        # Métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📊 Total", total)
        with col2:
            st.metric("🟢 Pagos", pagos)
        with col3:
            st.metric("🔔 A Cobrar", devedores)
        with col4:
            st.metric("🔴 Inadimplentes", inadimplentes)
        with col5:
            st.metric("💰 A Receber", f"R$ {valor_total:.2f}")
        
        st.markdown("---")
        
        # Ordenar pagamentos (mais recentes primeiro)
        pagamentos_filtrados.sort(key=lambda x: (x.get('ym', ''), x.get('alunoNome', '')), reverse=True)
        
        # Tabela compacta com st.dataframe
        STATUS_MAP = {
            'pago': '🟢 Pago',
            'devedor': '🔔 A Cobrar',
            'inadimplente': '🔴 Inadimplente',
            'ausente': '⚪ Ausente',
        }
        
        df_data = []
        for p in pagamentos_filtrados:
            df_data.append({
                'Aluno': p.get('alunoNome', 'N/A'),
                'Mês': p.get('ym', ''),
                'Valor': p.get('valor', 0),
                'Status': STATUS_MAP.get(p.get('status', ''), '❓ ' + p.get('status', '')),
                'Venc.': p.get('dataVencimento', 15),
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Valor': st.column_config.NumberColumn(format="R$ %.2f"),
                'Venc.': st.column_config.NumberColumn(format="Dia %d"),
            },
        )
        
        # Ações rápidas para pendentes (devedor / inadimplente)
        pendentes = [p for p in pagamentos_filtrados if p.get('status') in ('devedor', 'inadimplente')]
        if pendentes:
            st.markdown("#### ⚡ Ações Pendentes")
            cache_manager = get_cache_manager()
            for pag in pendentes:
                pag_id = pag.get('id', '')
                nome = pag.get('alunoNome', 'N/A')
                valor = pag.get('valor', 0)
                status = pag.get('status', '')
                emoji = '🔴' if status == 'inadimplente' else '🔔'
                
                c_info, c_pagar, c_editar = st.columns([5, 2, 1])
                with c_info:
                    st.markdown(f"{emoji} **{nome}** — {pag.get('ym', '')} — R$ {valor:.2f}")
                with c_pagar:
                    if st.button("💰 Pago", key=f"pag_pagar_{pag_id}", use_container_width=True):
                        try:
                            pagamentos_service.marcar_como_pago(pag_id)
                            cache_manager.invalidate_pagamento_cache(pag.get('ym'))
                            st.toast(f"✅ {nome} marcado como pago!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                with c_editar:
                    if st.button("✏️", key=f"edit_{pag_id}", help="Editar"):
                        st.session_state.pagamento_editando = pag_id
                        st.session_state.pagamentos_modo = 'editar'
                        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar pagamentos: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def _mostrar_lista_pagamentos(pagamentos_service: PagamentosService, alunos_service: AlunosService):
    """Mostra busca de alunos e seus pagamentos em painéis expansíveis"""
    
    st.markdown("### � Buscar Pagamentos por Aluno")
    
    # Campo de busca por nome do aluno
    col1, col2 = st.columns([3, 1])
    
    with col1:
        termo_busca = st.text_input(
            "Digite o nome do aluno:",
            placeholder="Ex: João Silva, Maria...",
            help="Digite pelo menos 2 caracteres para buscar",
            key="pag_busca_nome"
        )
    
    with col2:
        st.write("") # Spacer
    
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
            devedores = sum(1 for p in pagamentos_aluno if p.get('status') == 'devedor')
            inadimplentes = sum(1 for p in pagamentos_aluno if p.get('status') == 'inadimplente')
            
            # Painel expansível para cada aluno
            with st.expander(
                f"{status_emoji} {aluno_nome} - {total_pagamentos} pagamento(s) | ✅ {pagos} | 🔔 {devedores} | ❌ {inadimplentes}",
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
                    data_vencimento = pagamento.get('dataVencimento', 15)
                    
                    # Definir cor e emoji por status
                    if status == 'pago':
                        cor = "🟢"
                        status_texto = "Pago"
                    elif status == 'devedor':
                        cor = "🔔"
                        status_texto = "A Cobrar"
                    elif status == 'inadimplente':
                        cor = "🔴"
                        status_texto = "Inadimplente"
                    elif status == 'ausente':
                        cor = "🟡"
                        status_texto = "Ausente"
                    else:
                        cor = "⚪"
                        status_texto = "Indefinido"
                    
                    vencimento_info = f"Venc: {data_vencimento:02d}"
                    
                    # Layout compacto para cada pagamento
                    col_mes, col_status, col_valor, col_acoes = st.columns([2, 2, 2, 1])
                    
                    with col_mes:
                        st.write(f"📅 **{ym}**")
                    
                    with col_status:
                        st.write(f"{cor} **{status_texto}**")
                    
                    with col_valor:
                        st.write(f"💵 **R$ {valor:.2f}**")
                        st.caption(vencimento_info)
                    
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
                status_atual = pagamento.get('status', 'devedor')
                opcoes_status = ['pago', 'devedor', 'inadimplente', 'ausente']
                try:
                    index_status = opcoes_status.index(status_atual)
                except ValueError:
                    index_status = 1  # Default para 'devedor'
                
                novo_status = st.selectbox(
                    "📊 Status:",
                    options=opcoes_status,
                    index=index_status,
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
                
                # Dia de vencimento
                venc_atual = pagamento.get('dataVencimento', 15)
                novo_vencimento = st.selectbox(
                    "📅 Dia de Vencimento:",
                    options=[10, 15, 25],
                    index=[10, 15, 25].index(venc_atual) if venc_atual in [10, 15, 25] else 1,
                    help="Dia do mês para vencimento"
                )
            
            with col2:
                # Carência em dias
                carencia_atual = pagamento.get('carenciaDias', 3)
                nova_carencia = st.number_input(
                    "⏳ Carência (dias):",
                    min_value=0,
                    max_value=30,
                    value=int(carencia_atual),
                    help="Dias após vencimento antes de virar inadimplente"
                )
                
                # Data de vencimento (legado - remover depois)
                vencimento_atual = pagamento.get('vencimento', '')
                try:
                    data_vencimento_atual = datetime.strptime(vencimento_atual, '%Y-%m-%d').date() if vencimento_atual else date.today()
                except:
                    data_vencimento_atual = date.today()
                
                nova_data_vencimento = st.date_input(
                    "Data Vencimento:",
                    value=data_vencimento_atual,
                    format="DD/MM/YYYY"
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
                    "Data Pagamento:",
                    value=data_pag_inicial,
                    help="Data em que o pagamento foi realizado",
                    format="DD/MM/YYYY"
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
                            'dataVencimento': novo_vencimento,
                            'carenciaDias': nova_carencia
                        }
                        
                        # Manter campo vencimento antigo (legado)
                        if nova_data_vencimento:
                            dados_atualizacao['vencimento'] = nova_data_vencimento.strftime('%Y-%m-%d')
                        
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
                            # Invalidar cache de pagamentos
                            cache_manager = get_cache_manager()
                            cache_manager.invalidate_pagamento_cache(pagamento.get('ym'))
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
                            # Invalidar cache de pagamentos
                            cache_manager = get_cache_manager()
                            cache_manager.invalidate_pagamento_cache(pagamento.get('ym'))
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
    """Mostra formulário para registrar novo pagamento (status sempre 'pago')"""
    
    st.markdown("### ➕ Registrar Pagamento")
    
    # Mostrar sucesso se pagamento foi registrado
    if 'pagamento_registrado' in st.session_state:
        pagamento_info = st.session_state.pagamento_registrado
        st.success(f"✅ Pagamento de **{pagamento_info['aluno_nome']}** registrado!")
        st.info(f"💰 Valor: R$ {pagamento_info['valor']:.2f} — Referente a: {pagamento_info['ym']}")
        
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
    
    # Carregar alunos ativos e turmas FORA do form (para filtro de turma funcionar)
    try:
        alunos_ativos = alunos_service.listar_alunos(status='ativo')
        if not alunos_ativos:
            st.error("❌ Nenhum aluno ativo encontrado! Cadastre alunos primeiro.")
            return
    except Exception as e:
        st.error(f"❌ Erro ao carregar alunos: {str(e)}")
        return
    
    # Filtro por turma (fora do form para funcionar dinamicamente)
    turmas_existentes = sorted(list(set(a.get('turma', '') for a in alunos_ativos if a.get('turma'))))
    filtro_turma_opcoes = ["Todas as turmas"] + turmas_existentes
    filtro_turma = st.selectbox(
        "Filtrar por turma:",
        options=filtro_turma_opcoes,
        index=0,
        key="cadastrar_filtro_turma"
    )
    
    # Filtrar alunos pela turma selecionada
    if filtro_turma != "Todas as turmas":
        alunos_filtrados = [a for a in alunos_ativos if a.get('turma') == filtro_turma]
    else:
        alunos_filtrados = alunos_ativos
    
    alunos_filtrados.sort(key=lambda a: a.get('nome', ''))
    alunos_opcoes = {a['nome']: a['id'] for a in alunos_filtrados}
    
    if not alunos_opcoes:
        st.warning("Nenhum aluno encontrado nesta turma.")
        return
    
    with st.form("form_novo_pagamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            aluno_selecionado = st.selectbox(
                "Aluno *",
                options=list(alunos_opcoes.keys()),
                help="Selecione o aluno"
            )
            
            hoje = date.today()
            modo = st.session_state.get('data_mode', 'operacional')
            min_ano_ref = 2026 if modo == 'operacional' else 2020
            
            _nomes_meses = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            opcoes_ym = []
            for a in range(min_ano_ref, hoje.year + 1):
                for m in range(1, 13):
                    if a == hoje.year and m > hoje.month:
                        break
                    opcoes_ym.append((a, m, f"{a}-{m:02d} ({_nomes_meses[m]})"))
            
            default_idx = next(
                (i for i, (a, m, _) in enumerate(opcoes_ym) if a == max(hoje.year, min_ano_ref) and m == hoje.month),
                0
            )
            ym_selecionado = st.selectbox(
                "Mês/Ano de Referência *",
                options=opcoes_ym,
                index=default_idx,
                format_func=lambda x: x[2],
            )
            ano_ref = ym_selecionado[0]
            mes_ref = ym_selecionado[1]
        
        with col2:
            valor = st.number_input("Valor (R$) *", min_value=0.01, step=0.01, format="%.2f", value=150.0)
        
        st.markdown("---")
        submitted = st.form_submit_button("✅ Registrar Pagamento", type="primary", use_container_width=True)
        
        if submitted:
            if not aluno_selecionado:
                st.error("❌ Selecione um aluno!")
                return
            
            if valor <= 0:
                st.error("❌ Valor deve ser maior que zero!")
                return
            
            aluno_id = alunos_opcoes[aluno_selecionado]
            
            try:
                aluno = alunos_service.buscar_aluno(aluno_id)
                if not aluno:
                    st.error("❌ Aluno não encontrado!")
                    return
                aluno_nome = aluno.get('nome', 'N/A')
            except Exception as e:
                st.error(f"❌ Erro ao buscar aluno: {str(e)}")
                return
            
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
            
            dados_pagamento = {
                'alunoId': aluno_id,
                'alunoNome': aluno_nome,
                'ano': ano_ref,
                'mes': mes_ref,
                'valor': valor,
                'status': 'pago',
                'exigivel': True
            }
            
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

def _mostrar_devedores(pagamentos_service: PagamentosService):
    """
    Mostra lista automática de 'A Cobrar' baseada na data atual.
    
    Regra progressiva por dia do mês:
    - Dia 1 a 10: mostra alunos com vencimento dia 10 que NÃO pagaram
    - Dia 11 a 15: mostra alunos com vencimento dia 15 que NÃO pagaram
    - Dia 16 a 25: mostra alunos com vencimento dia 25 que NÃO pagaram
    
    Alunos que já passaram do vencimento e não pagaram vão para Inadimplentes.
    """
    
    st.markdown("### 🔔 A Cobrar")
    
    hoje = date.today()
    dia_atual = hoje.day
    mes_atual = hoje.month
    ano_atual = hoje.year
    ym_atual = f"{ano_atual:04d}-{mes_atual:02d}"
    
    # Determinar qual grupo de vencimento está "a cobrar" agora
    if dia_atual <= 10:
        vencimento_alvo = 10
        label_periodo = f"Vencimento dia 10 (estamos no dia {dia_atual})"
    elif dia_atual <= 15:
        vencimento_alvo = 15
        label_periodo = f"Vencimento dia 15 (estamos no dia {dia_atual})"
    elif dia_atual <= 25:
        vencimento_alvo = 25
        label_periodo = f"Vencimento dia 25 (estamos no dia {dia_atual})"
    else:
        # Após dia 25, todos os vencimentos do mês já passaram
        st.info("📅 Todos os vencimentos do mês já passaram. Verifique a aba **Inadimplentes** para pendências.")
        return
    
    st.caption(f"📅 {label_periodo}")
    
    try:
        # 1. Buscar todos os alunos ativos
        if 'alunos_service' not in st.session_state:
            st.session_state.alunos_service = AlunosService()
        alunos_service = st.session_state.alunos_service
        alunos_ativos = alunos_service.listar_alunos(status='ativo')
        
        if not alunos_ativos:
            st.info("Nenhum aluno ativo cadastrado.")
            return
        
        # 2. Buscar pagamentos do mês corrente
        pagamentos_mes = pagamentos_service.listar_pagamentos(filtros={'ym': ym_atual})
        alunos_com_pagamento = {p.get('alunoId') for p in pagamentos_mes if p.get('status') == 'pago'}
        
        # 3. Filtrar alunos a cobrar: vencimento == alvo E sem pagamento pago
        a_cobrar = []
        for aluno in alunos_ativos:
            aluno_id = aluno.get('id')
            venc_dia = int(aluno.get('vencimentoDia', 15))
            
            # Só mostra se o vencimento corresponde ao grupo atual
            if venc_dia != vencimento_alvo:
                continue
            
            # Só mostra se NÃO tem pagamento pago no mês
            if aluno_id in alunos_com_pagamento:
                continue
            
            a_cobrar.append(aluno)
        
        if not a_cobrar:
            st.success(f"🎉 Todos os alunos com vencimento dia {vencimento_alvo} estão em dia!")
            return
        
        # Métricas
        st.warning(f"🔔 **{len(a_cobrar)} aluno(s) a cobrar** — vencimento dia {vencimento_alvo}")
        
        dias_restantes = vencimento_alvo - dia_atual
        if dias_restantes > 0:
            st.info(f"⏰ Faltam **{dias_restantes} dia(s)** para o vencimento")
        elif dias_restantes == 0:
            st.error("⚠️ **Hoje é o dia do vencimento!**")
        
        # Lista de alunos a cobrar
        cache_manager = get_cache_manager()
        for aluno in sorted(a_cobrar, key=lambda a: a.get('nome', '')):
            aluno_id = aluno.get('id')
            nome = aluno.get('nome', 'N/A')
            turma = aluno.get('turma', '—')
            contato = aluno.get('contato', {})
            telefone = contato.get('telefone', '') if isinstance(contato, dict) else ''
            
            with st.container(border=True):
                c_info, c_turma, c_acao = st.columns([4, 2, 2])
                with c_info:
                    st.markdown(f"🔔 **{nome}**")
                    if telefone:
                        tel_limpo = ''.join(c for c in telefone if c.isdigit())
                        st.caption(f"📱 [{telefone}](https://wa.me/55{tel_limpo})")
                with c_turma:
                    st.caption(f"Turma: {turma}")
                    st.caption(f"Venc: dia {vencimento_alvo}")
                with c_acao:
                    if st.button("💰 Registrar Pgto", key=f"cobrar_{aluno_id}", use_container_width=True):
                        st.session_state.current_page = "👥 Alunos"
                        st.session_state.alunos_modo = 'lista'
                        st.session_state.busca_aluno_id = aluno_id
                        st.session_state.ficha_tab_default = 'pagamentos'
                        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar a cobrar: {str(e)}")

def _mostrar_inadimplentes(pagamentos_service: PagamentosService):
    """
    Mostra inadimplentes: alunos que passaram do dia de vencimento
    e NÃO possuem pagamento 'pago' para o mês corrente.
    
    Regra: Se hoje > dia de vencimento do aluno e não tem pagamento pago → inadimplente.
    - Dia 11: alunos com vencimento dia 10 sem pagamento → inadimplentes
    - Dia 16: alunos com vencimento dia 10 e 15 sem pagamento → inadimplentes
    - Dia 26: alunos com vencimento dia 10, 15 e 25 sem pagamento → inadimplentes
    """
    
    st.markdown("### 🔴 Inadimplentes")
    
    hoje = date.today()
    dia_atual = hoje.day
    mes_atual = hoje.month
    ano_atual = hoje.year
    ym_atual = f"{ano_atual:04d}-{mes_atual:02d}"
    
    # Determinar quais vencimentos já passaram
    vencimentos_passados = [v for v in [10, 15, 25] if dia_atual > v]
    
    if not vencimentos_passados:
        st.success("🎉 Nenhum vencimento ultrapassado até agora neste mês. Ainda estamos antes do dia 10.")
        return
    
    st.caption(f"📅 Verificando vencimentos já ultrapassados: dias {', '.join(str(v) for v in vencimentos_passados)} (hoje é dia {dia_atual})")
    
    try:
        # 1. Buscar todos os alunos ativos
        if 'alunos_service' not in st.session_state:
            st.session_state.alunos_service = AlunosService()
        alunos_service = st.session_state.alunos_service
        alunos_ativos = alunos_service.listar_alunos(status='ativo')
        
        if not alunos_ativos:
            st.info("Nenhum aluno ativo cadastrado.")
            return
        
        # 2. Buscar pagamentos do mês corrente
        pagamentos_mes = pagamentos_service.listar_pagamentos(filtros={'ym': ym_atual})
        alunos_com_pagamento = {p.get('alunoId') for p in pagamentos_mes if p.get('status') == 'pago'}
        
        # 3. Filtrar inadimplentes: vencimento já passou E sem pagamento pago
        inadimplentes = []
        for aluno in alunos_ativos:
            aluno_id = aluno.get('id')
            venc_dia = int(aluno.get('vencimentoDia', 15))
            
            # Só é inadimplente se o vencimento JÁ PASSOU
            if venc_dia not in vencimentos_passados:
                continue
            
            # Só é inadimplente se NÃO tem pagamento pago
            if aluno_id in alunos_com_pagamento:
                continue
            
            aluno['_dias_atraso'] = dia_atual - venc_dia
            inadimplentes.append(aluno)
        
        if not inadimplentes:
            st.success("🎉 Nenhum inadimplente! Todos os alunos com vencimento passado já pagaram.")
            return
        
        # Métricas
        st.error(f"⚠️ **{len(inadimplentes)} aluno(s) inadimplente(s)** no mês de {ym_atual}")
        
        # Agrupar por dia de vencimento
        por_vencimento = {}
        for aluno in inadimplentes:
            venc = int(aluno.get('vencimentoDia', 15))
            if venc not in por_vencimento:
                por_vencimento[venc] = []
            por_vencimento[venc].append(aluno)
        
        cache_manager = get_cache_manager()
        
        for venc_dia in sorted(por_vencimento.keys()):
            grupo = por_vencimento[venc_dia]
            dias_atraso = dia_atual - venc_dia
            st.markdown(f"#### Vencimento dia {venc_dia} — {dias_atraso} dia(s) em atraso ({len(grupo)} aluno(s))")
            
            for aluno in sorted(grupo, key=lambda a: a.get('nome', '')):
                aluno_id = aluno.get('id')
                nome = aluno.get('nome', 'N/A')
                turma = aluno.get('turma', '—')
                contato = aluno.get('contato', {})
                telefone = contato.get('telefone', '') if isinstance(contato, dict) else ''
                
                with st.container(border=True):
                    c_info, c_turma, c_acao = st.columns([4, 2, 2])
                    with c_info:
                        st.markdown(f"🔴 **{nome}**")
                        if telefone:
                            tel_limpo = ''.join(c for c in telefone if c.isdigit())
                            st.caption(f"📱 [{telefone}](https://wa.me/55{tel_limpo})")
                    with c_turma:
                        st.caption(f"Turma: {turma}")
                        st.caption(f"Atraso: {aluno.get('_dias_atraso', 0)} dia(s)")
                    with c_acao:
                        if st.button("💰 Registrar Pgto", key=f"inadim_{aluno_id}", use_container_width=True):
                            st.session_state.current_page = "👥 Alunos"
                            st.session_state.alunos_modo = 'lista'
                            st.session_state.busca_aluno_id = aluno_id
                            st.session_state.ficha_tab_default = 'pagamentos'
                            st.rerun()
    
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

        modo = st.session_state.get('data_mode', 'operacional')
        min_ym = "2026-01" if modo == 'operacional' else "2024-01"
        
        # Gerar opções de mês
        meses_opcoes = []
        for i in range(12):
            mes = hoje.month - i
            ano = hoje.year
            if mes <= 0:
                mes += 12
                ano -= 1
            mes_ano = f"{ano:04d}-{mes:02d}"

            if mes_ano < min_ym:
                continue

            meses_opcoes.append(mes_ano)

        if not meses_opcoes:
            meses_opcoes = [f"{hoje.year:04d}-{hoje.month:02d}"]
        
        ym_stats = st.selectbox("📅 Mês para análise:", options=meses_opcoes, index=0)
    
    # Obter estatísticas
    try:
        stats = pagamentos_service.obter_estatisticas_mes(ym_stats)
        
        # Exibir métricas principais
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="💰 Receita Total",
                value=f"R$ {stats['receita_total']:.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="✅ Pagos",
                value=stats['total_pagos'],
                delta=f"{stats['total_pagos']}/{stats['total_pagamentos']}"
            )
        
        with col3:
            st.metric(
                label="🔔 A Cobrar",
                value=stats.get('total_devedores', 0),
                delta=f"R$ {stats.get('valor_devedores', 0):.2f}"
            )
        
        with col4:
            st.metric(
                label="🚫 Inadimplentes",
                value=stats['total_inadimplentes'],
                delta=f"R$ {stats['valor_inadimplencia']:.2f}"
            )
        
        with col5:
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
                'Status': ['Pagos', 'A Cobrar', 'Inadimplentes', 'Ausentes'],
                'Quantidade': [
                    stats['total_pagos'], 
                    stats.get('total_devedores', 0),
                    stats['total_inadimplentes'], 
                    stats['total_ausentes']
                ],
                'Valor': [
                    stats['receita_total'], 
                    stats.get('valor_devedores', 0),
                    stats['valor_inadimplencia'], 
                    0
                ]
            })
            
            max_qtd = chart_data['Quantidade'].max()
            for _, row in chart_data.iterrows():
                col_n, col_b, col_v = st.columns([2, 5, 1])
                with col_n:
                    st.markdown(f"**{row['Status']}**")
                with col_b:
                    st.progress(row['Quantidade'] / max_qtd if max_qtd > 0 else 0)
                with col_v:
                    st.markdown(f"**{int(row['Quantidade'])}**")
        
        with col2:
            st.markdown("#### 💵 Valores por Status")
            max_val = chart_data['Valor'].max()
            for _, row in chart_data.iterrows():
                col_n, col_b, col_v = st.columns([2, 5, 1])
                with col_n:
                    st.markdown(f"**{row['Status']}**")
                with col_b:
                    st.progress(row['Valor'] / max_val if max_val > 0 else 0)
                with col_v:
                    st.markdown(f"**R$ {row['Valor']:.0f}**")
        
        # Lista detalhada
        if st.checkbox("📋 Mostrar detalhes dos pagamentos"):
            st.markdown("#### 📋 Detalhes dos Pagamentos")
            
            tab1, tab2, tab3, tab4 = st.tabs(["✅ Pagos", "🔔 A Cobrar", "🚫 Inadimplentes", "⚪ Ausentes"])
            
            with tab1:
                pagos = stats['detalhes']['pagos']
                if pagos:
                    for p in pagos:
                        st.write(f"✅ {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f}")
                else:
                    st.info("Nenhum pagamento confirmado")
            
            with tab2:
                devedores = stats['detalhes'].get('devedores', [])
                if devedores:
                    for p in devedores:
                        venc = p.get('dataVencimento', 15)
                        st.write(f"🔔 {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f} (Venc: {venc:02d})")
                else:
                    st.success("Nenhum devedor! 🎉")
            
            with tab3:
                inadimplentes = stats['detalhes']['inadimplentes']
                if inadimplentes:
                    for p in inadimplentes:
                        st.write(f"🚫 {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f}")
                else:
                    st.success("Nenhum inadimplente! 🎉")
            
            with tab4:
                ausentes = stats['detalhes']['ausentes']
                if ausentes:
                    for p in ausentes:
                        st.write(f"⚪ {p.get('alunoNome', 'N/A')} - R$ {p.get('valor', 0):.2f}")
                else:
                    st.info("Nenhum ausente registrado")
        
    except Exception as e:
        st.error(f"❌ Erro ao obter estatísticas: {str(e)}")

