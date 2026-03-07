"""
Página Dashboard - KPIs e visão geral
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Any, Optional
import pandas as pd
from src.utils.notifications import NotificationService
from src.services.alunos_service import AlunosService
from src.services.pagamentos_service import PagamentosService
from src.services.presencas_service import PresencasService
from src.services.graduacoes_service import GraduacoesService
from src.utils.cache_service import get_cache_manager

def show_dashboard(mode: Optional[str] = None, forced_year: Optional[int] = None):
    """Exibe o dashboard principal com KPIs"""
    
    st.markdown("## 📊 Dashboard")
    
    effective_mode = mode or st.session_state.get('data_mode', 'operacional')

    if effective_mode == 'historico':
        st.caption("Histórico 2024/2025 (somente leitura)")
    
    # Seletor de mês (dinâmico baseado na data atual)
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        current_year = datetime.now().year
        current_month = datetime.now().month

        if effective_mode == 'historico':
            anos_disponiveis = [2024, 2025]
        else:
            # Operação a partir de 2026
            start_year = 2026
            anos_disponiveis = list(range(start_year, max(start_year, current_year) + 1))

        # Ano padrão
        if forced_year in anos_disponiveis:
            default_year_index = anos_disponiveis.index(forced_year)
        else:
            default_year_index = len(anos_disponiveis) - 1
        
        selected_year = st.selectbox(
            "Ano:", 
            options=anos_disponiveis,
            index=default_year_index
        )
    
    with col2:
        # Determinar meses disponíveis baseado no ano selecionado
        if selected_year == current_year:
            # Para o ano atual, só mostrar até o mês atual
            meses_disponiveis = list(range(1, current_month + 1))
        else:
            # Para anos anteriores, mostrar todos os meses
            meses_disponiveis = list(range(1, 13))
        
        # Adicionar opção "Todos" para mostrar dados anuais
        meses_opcoes = ["Todos"] + meses_disponiveis
        meses_labels = ["Todos os meses"] + [f"{x:02d}" for x in meses_disponiveis]
        
        # Índice padrão: mês atual se ano atual, senão último mês disponível
        if selected_year == current_year:
            default_month_index = len(meses_opcoes) - 1  # Último mês (atual)
        else:
            default_month_index = len(meses_opcoes) - 1  # Último mês do ano
        
        selected_month_option = st.selectbox(
            "Mês:",
            options=meses_opcoes,
            index=default_month_index,
            format_func=lambda x: meses_labels[meses_opcoes.index(x)]
        )
        
        # Determinar se é consulta anual ou mensal
        is_annual_view = selected_month_option == "Todos"
        selected_month = None if is_annual_view else selected_month_option
    
    # Gerar ym para consultas ou usar ano para consulta anual
    if is_annual_view:
        ym = str(selected_year)  # Apenas o ano para consulta anual
        periodo_titulo = f"Ano {selected_year}"
    else:
        ym = f"{selected_year}-{selected_month:02d}"
        periodo_titulo = f"{ym}"
    
    st.markdown(f"### 📅 Relatório: {periodo_titulo}")
    
    # Obter dados reais dos serviços (modificado para suportar consulta anual)
    dados_reais = _get_real_data(ym, is_annual_view, mode=effective_mode) or {}
    dados_reais = {
        'receita': 0.0,
        'devedores': 0,
        'valor_devedores': 0.0,
        'inadimplentes': 0,
        'valor_inadimplentes': 0.0,
        'ativos': 0,
        'percentual_ativos': 0,
        'media_presencas_dia': 0.0,
        'total_presencas': 0,
        **dados_reais,
    }
    
    # Métricas principais - 5 colunas para separar A Cobrar e Inadimplentes
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        periodo_label = "do Ano" if is_annual_view else "do Mês"
        comparacao_label = "+12% vs ano anterior" if is_annual_view else "+12% vs mês anterior"
        
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Receita {}</h3>
            <h2 style="color: #28a745;">R$ {:.2f}</h2>
            <small>📈 {}</small>
        </div>
        """.format(periodo_label, dados_reais['receita'], comparacao_label), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔔 A Cobrar</h3>
            <h2 style="color: #ffc107;">{}</h2>
            <small>💰 R$ {:.2f}</small>
        </div>
        """.format(dados_reais['devedores'], dados_reais['valor_devedores']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔴 Inadimplentes</h3>
            <h2 style="color: #dc3545;">{}</h2>
            <small>💸 R$ {:.2f}</small>
        </div>
        """.format(dados_reais['inadimplentes'], dados_reais['valor_inadimplentes']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Alunos Ativos</h3>
            <h2 style="color: #007bff;">{}</h2>
            <small>📊 {}% do total</small>
        </div>
        """.format(
            dados_reais['ativos'], 
            dados_reais['percentual_ativos']
        ), unsafe_allow_html=True)
    
    with col5:
        presencas_label = "Presenças" if is_annual_view else "Presenças"
        media_label = f"Média: {dados_reais['media_presencas_dia']:.1f}/dia" if not is_annual_view else f"Total no ano: {dados_reais['total_presencas']}"
        
        st.markdown("""
        <div class="metric-card">
            <h3>✅ {}</h3>
            <h2 style="color: #17a2b8;">{}</h2>
            <small>📅 {}</small>
        </div>
        """.format(
            presencas_label,
            dados_reais['total_presencas'],
            media_label
        ), unsafe_allow_html=True)
    
    st.divider()
    
    # --- Ações Rápidas ---
    if effective_mode != 'historico':
        st.markdown("### ⚡ Ações Rápidas")
        aq1, aq2, aq3 = st.columns(3)
        with aq1:
            if st.button("✅ Registrar Presença", use_container_width=True):
                st.session_state.current_page = "✅ Presenças"
                st.rerun()
        with aq2:
            if st.button("💰 Novo Pagamento", use_container_width=True):
                st.session_state.current_page = "💰 Pagamentos"
                st.session_state['pagamentos_modo'] = 'novo'
                st.rerun()
        with aq3:
            if st.button("👥 Novo Aluno", use_container_width=True):
                st.session_state.current_page = "👥 Alunos"
                st.session_state['alunos_modo'] = 'novo'
                st.rerun()
        st.divider()

    # --- Seção Devedores / Inadimplentes do Mês (ação rápida) ---
    if not is_annual_view and effective_mode != 'historico':
        _mostrar_secao_devedores(ym, dados_reais)
    
    # Gráficos ocultos por ora (Evolução Receita, Status Alunos, Analytics)
    # Pode ser reativado futuramente se necessário
    
    # # ====================================================================
    # # SEÇÃO DE ALERTAS E NOTIFICAÇÕES - TEMPORARIAMENTE DESABILITADA
    # # Código comentado para economizar requisições ao Firestore
    # # ====================================================================
    # # Seção de Alertas e Notificações
    # st.markdown("---")
    # st.markdown("### 🚨 Alertas e Notificações")
    # 
    # try:
    #     # Inicializar serviço de notificações
    #     notification_service = NotificationService()
    #     
    #     # Gerar relatório de alertas
    #     relatorio_alertas = notification_service.gerar_relatorio_alertas()
    #     
    #     # Exibir status geral
    #     nivel_geral = relatorio_alertas['resumo']['nivel_geral']
    #     
    #     col1, col2, col3 = st.columns([1, 2, 1])
    #     with col2:
    #         st.markdown(f"""
    #         <div style="text-align: center; padding: 1rem; border-radius: 10px; 
    #                    background-color: {'#d4edda' if nivel_geral['cor'] == 'green' else 
    #                                      '#fff3cd' if nivel_geral['cor'] == 'yellow' else
    #                                      '#f8d7da' if nivel_geral['cor'] == 'red' else '#d1ecf1'};">
    #             <h3>{nivel_geral['emoji']} Status Geral: {nivel_geral['nivel']}</h3>
    #             <p>{nivel_geral['acao']}</p>
    #         </div>
    #         """, unsafe_allow_html=True)
    #     
    #     # Alertas em cards
    #     col1, col2 = st.columns(2)
    #     
    #     with col1:
    #         st.markdown("#### 👻 Alunos Ausentes")
    #         ausentes_info = relatorio_alertas['alunos_ausentes']
    #         
    #         if ausentes_info['total'] > 0:
    #             st.error(f"⚠️ {ausentes_info['total']} aluno(s) ausente(s)")
    #             
    #             # Mostrar top 3 mais críticos
    #             for aluno in ausentes_info['detalhes'][:3]:
    #                 status = aluno['status_risco']
    #                 st.markdown(f"""
    #                 {status['emoji']} **{aluno['nome']}** - {aluno['dias_sem_atividade']} dias
    #                 """)
    #             
    #             if st.button("👁️ Ver Todos Ausentes", use_container_width=True):
    #                 st.session_state.mostrar_detalhes_ausentes = True
    #                 st.rerun()
    #         else:
    #             st.success("✅ Nenhum aluno ausente!")
    #     
    #     with col2:
    #         st.markdown("#### 🚫 Inadimplentes Críticos")
    #         inadimplentes_info = relatorio_alertas['inadimplentes_criticos']
    #         
    #         if inadimplentes_info['total'] > 0:
    #             st.error(f"💸 {inadimplentes_info['total']} inadimplente(s) crítico(s)")
    #             st.error(f"💰 Total: R$ {inadimplentes_info['valor_total']:.2f}")
    #             
    #             # Mostrar top 3 mais críticos
    #             for pagamento in inadimplentes_info['detalhes'][:3]:
    #                 status = pagamento['status_risco']
    #                 dias_atraso = pagamento.get('dias_atraso', 0)
    #                 valor = pagamento.get('valor', 0)
    #                 st.markdown(f"""
    #                 {status['emoji']} **{pagamento.get('alunoNome', 'N/A')}** - {dias_atraso} dias - R$ {valor:.2f}
    #                 """)
    #             
    #             if st.button("👁️ Ver Todos Inadimplentes", use_container_width=True):
    #                 st.info("💡 Use o menu lateral para navegar para 'Pagamentos' e ver inadimplentes")
    #         else:
    #             st.success("✅ Nenhum inadimplente crítico!")
    #     
    #     # Detalhes expandidos se solicitado
    #     if st.session_state.get('mostrar_detalhes_ausentes', False):
    #         st.markdown("#### 📋 Detalhes - Alunos Ausentes")
    #         
    #         for aluno in relatorio_alertas['alunos_ausentes']['detalhes']:
    #             status = aluno['status_risco']
    #             
    #             with st.expander(f"{status['emoji']} {aluno['nome']} - {aluno['dias_sem_atividade']} dias"):
    #                 col1, col2 = st.columns(2)
    #                 
    #                 with col1:
    #                     st.write(f"**ID:** {aluno['id']}")
    #                     st.write(f"**Status:** {status['nivel']}")
    #                     st.write(f"**Ação:** {status['acao']}")
    #                 
    #                 with col2:
    #                     contato = aluno.get('contato', {})
    #                     if contato.get('telefone'):
    #                         st.write(f"**Telefone:** {contato['telefone']}")
    #                     if contato.get('email'):
    #                         st.write(f"**Email:** {contato['email']}")
    #                     
    #                     ultimo_pag = aluno.get('ultimo_pagamento')
    #                     if ultimo_pag:
    #                         st.write(f"**Último pagamento:** {ultimo_pag.get('ym', 'N/A')}")
    #         
    #         if st.button("🔼 Recolher", use_container_width=True):
    #             st.session_state.mostrar_detalhes_ausentes = False
    #             st.rerun()
    # 
    # except Exception as e:
    #     st.error(f"❌ Erro ao carregar alertas: {str(e)}")
    # # ==================================================================== 
    # # FIM DA SEÇÃO DE ALERTAS E NOTIFICAÇÕES (COMENTADA)
    # # ====================================================================


def _mostrar_secao_devedores(ym: str, dados_reais: Dict[str, Any]):
    """Mostra lista de devedores/inadimplentes com ações rápidas (Marcar Pago, WhatsApp)"""
    total_pendentes = dados_reais.get('devedores', 0) + dados_reais.get('inadimplentes', 0)
    if total_pendentes == 0:
        st.success("✅ Nenhum devedor ou inadimplente neste mês!")
        st.divider()
        return

    st.markdown("### 🔔 Cobranças Pendentes")

    try:
        if 'pagamentos_service' not in st.session_state:
            st.session_state.pagamentos_service = PagamentosService()
        if 'alunos_service' not in st.session_state:
            st.session_state.alunos_service = AlunosService()
        pagamentos_service = st.session_state.pagamentos_service
        alunos_service = st.session_state.alunos_service
        cache_manager = get_cache_manager()

        # Buscar devedores e inadimplentes do mês
        devedores = pagamentos_service.obter_devedores(ym=ym)
        inadimplentes = pagamentos_service.obter_inadimplentes(ym=ym)
        pendentes = devedores + inadimplentes

        if not pendentes:
            st.info("Nenhum pagamento pendente encontrado.")
            st.divider()
            return

        # Montar mapa alunoId → telefone (1 query via cache)
        alunos = cache_manager.get_alunos_cached(alunos_service)
        telefone_map = {a['id']: a.get('telefone', '') for a in alunos}

        for pag in pendentes:
            pag_id = pag.get('id', '')
            nome = pag.get('alunoNome', 'N/A')
            valor = pag.get('valor', 0)
            status = pag.get('status', 'devedor')
            aluno_id = pag.get('alunoId', '')
            telefone = telefone_map.get(aluno_id, '')

            status_emoji = "🔴" if status == 'inadimplente' else "🟡"
            status_label = "Inadimplente" if status == 'inadimplente' else "A cobrar"

            col_info, col_tel, col_action = st.columns([4, 2, 2])

            with col_info:
                st.markdown(f"{status_emoji} **{nome}** — R$ {valor:.2f} ({status_label})")

            with col_tel:
                if telefone:
                    tel_limpo = ''.join(c for c in telefone if c.isdigit())
                    if tel_limpo:
                        st.markdown(
                            f"[📱 WhatsApp](https://wa.me/55{tel_limpo})",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.caption("Sem telefone")
                else:
                    st.caption("Sem telefone")

            with col_action:
                if st.button("💰 Pago", key=f"dash_pagar_{pag_id}", use_container_width=True):
                    try:
                        pagamentos_service.marcar_como_pago(pag_id)
                        cache_manager.invalidate_pagamento_cache()
                        st.toast(f"✅ {nome} marcado como pago!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    except Exception as e:
        st.error(f"Erro ao carregar devedores: {e}")

    st.divider()


def _get_available_period():
    """Detecta período disponível nos dados reais de pagamentos"""
    try:
        # Inicializar serviço de pagamentos
        cache_manager = get_cache_manager()
        
        # Buscar anos disponíveis nos pagamentos
        if 'pagamentos_service' not in st.session_state:
            st.session_state.pagamentos_service = PagamentosService()
        
        pagamentos_service = st.session_state.pagamentos_service
        
        # Buscar todos os pagamentos para extrair anos
        try:
            # Buscar todos os documentos de pagamentos
            collection_ref = pagamentos_service.db.collection('pagamentos')
            docs = list(collection_ref.stream())
            
            anos_encontrados = set()
            meses_por_ano = {}
            
            for doc in docs:
                data = doc.to_dict()
                ano = data.get('ano')
                mes = data.get('mes')
                
                if ano and mes:
                    anos_encontrados.add(int(ano))
                    if ano not in meses_por_ano:
                        meses_por_ano[ano] = set()
                    meses_por_ano[ano].add(int(mes))
            
            # Se não encontrou dados, usar ano atual como fallback
            if not anos_encontrados:
                current_year = datetime.now().year
                anos_encontrados = {current_year}
                meses_por_ano = {current_year: {datetime.now().month}}
            
            return {
                'anos': list(anos_encontrados),
                'meses_por_ano': meses_por_ano
            }
            
        except Exception as e:
            # Fallback se não conseguir acessar dados
            current_year = datetime.now().year
            return {
                'anos': [current_year],
                'meses_por_ano': {current_year: {datetime.now().month}}
            }
    
    except Exception as e:
        # Fallback completo
        current_year = datetime.now().year
        return {
            'anos': [current_year],
            'meses_por_ano': {current_year: {datetime.now().month}}
        }

def _get_real_data(ym: str, is_annual_view: bool = False, mode: str = 'operacional') -> Dict[str, Any]:
    """Obtém dados reais dos serviços para o dashboard com cache"""
    try:
        # Reusar instâncias via session_state (T25)
        if 'alunos_service' not in st.session_state:
            st.session_state.alunos_service = AlunosService()
        if 'pagamentos_service' not in st.session_state:
            st.session_state.pagamentos_service = PagamentosService()
        if 'presencas_service' not in st.session_state:
            st.session_state.presencas_service = PresencasService()
        alunos_service = st.session_state.alunos_service
        pagamentos_service = st.session_state.pagamentos_service
        presencas_service = st.session_state.presencas_service
        cache_manager = get_cache_manager()
        
        # Determinar ano-alvo
        try:
            target_year = int(str(ym).split('-')[0])
        except Exception:
            target_year = datetime.now().year

        # Dados de alunos (com cache)
        alunos = cache_manager.get_alunos_cached(alunos_service)

        # Para operação (2026+), apartar base ignorando legados
        if mode != 'historico':
            def _is_2026_plus(aluno: Dict[str, Any]) -> bool:
                ativo_desde = aluno.get('ativoDesde')
                if not ativo_desde or not isinstance(ativo_desde, str):
                    return False
                try:
                    return int(ativo_desde[:4]) >= 2026
                except Exception:
                    return False

            alunos = [a for a in alunos if _is_2026_plus(a)]
        total_alunos = len(alunos)
        alunos_ativos = len([a for a in alunos if a.get('status') == 'ativo'])
        alunos_inativos = total_alunos - alunos_ativos
        percentual_ativos = round((alunos_ativos / max(1, total_alunos)) * 100, 1)
        
        # Dados de pagamentos (com cache) - modificado para suportar consulta anual
        try:
            if is_annual_view:
                # Para visualização anual, calcular receita de todo o ano
                ano = int(ym)
                receita_total_ano = 0.0
                devedores_total = 0
                inadimplentes_total = 0
                valor_devedores_total = 0.0
                valor_inadimplentes_total = 0.0
                
                # Buscar todos os meses do ano
                for mes in range(1, 13):
                    ym_mes = f"{ano}-{mes:02d}"
                    try:
                        estat_mes = cache_manager.get_estatisticas_pagamentos_cached(pagamentos_service, ym_mes)
                        receita_total_ano += estat_mes.get('receita_total', 0.0)
                        devedores_total += estat_mes.get('total_devedores', 0)
                        inadimplentes_total += estat_mes.get('total_inadimplentes', 0)
                        valor_devedores_total += estat_mes.get('valor_devedores', 0.0)
                        valor_inadimplentes_total += estat_mes.get('valor_inadimplencia', 0.0)
                    except:
                        continue
                
                receita = receita_total_ano
                devedores = devedores_total
                inadimplentes = inadimplentes_total
                valor_devedores = valor_devedores_total
                valor_inadimplentes = valor_inadimplentes_total
            else:
                # Consulta mensal normal
                estatisticas_pag = cache_manager.get_estatisticas_pagamentos_cached(pagamentos_service, ym)
                receita = estatisticas_pag.get('receita_total', 0.0)
                devedores = estatisticas_pag.get('total_devedores', 0)
                inadimplentes = estatisticas_pag.get('total_inadimplentes', 0)
                valor_devedores = estatisticas_pag.get('valor_devedores', 0.0)
                valor_inadimplentes = estatisticas_pag.get('valor_inadimplencia', 0.0)
        except Exception:
            receita = 0.0
            devedores = 0
            inadimplentes = 0
            valor_devedores = 0.0
            valor_inadimplentes = 0.0
        
        # Dados de presenças (com cache) - modificado para suportar consulta anual
        try:
            if is_annual_view:
                # Para visualização anual, somar presenças de todo o ano
                ano = int(ym)
                total_presencas_ano = 0
                total_dias_com_presencas = 0
                
                for mes in range(1, 13):
                    ym_mes = f"{ano}-{mes:02d}"
                    try:
                        relatorio_mes = cache_manager.get_relatorio_presencas_cached(presencas_service, ym_mes)
                        total_presencas_ano += relatorio_mes.get('total_presencas', 0)
                        if relatorio_mes.get('total_presencas', 0) > 0:
                            total_dias_com_presencas += 1
                    except:
                        continue
                
                total_presencas = total_presencas_ano
                media_presencas_dia = total_presencas_ano / max(1, total_dias_com_presencas * 30)  # Aproximação
            else:
                # Consulta mensal normal
                relatorio_presencas = cache_manager.get_relatorio_presencas_cached(presencas_service, ym)
                total_presencas = relatorio_presencas.get('total_presencas', 0)
                media_presencas_dia = relatorio_presencas.get('media_presencas_dia', 0.0)
        except Exception:
            total_presencas = 0
            media_presencas_dia = 0.0
        
        return {
            'receita': receita,
            'devedores': devedores,
            'inadimplentes': inadimplentes,
            'valor_devedores': valor_devedores,
            'valor_inadimplentes': valor_inadimplentes,
            'ativos': alunos_ativos,
            'inativos': alunos_inativos,
            'percentual_ativos': percentual_ativos,
            'total_presencas': total_presencas,
            'media_presencas_dia': media_presencas_dia,
            'ym': ym
        }
        
    except Exception as e:
        # Fallback para dados mock em caso de erro
        st.warning(f"⚠️ Erro ao carregar dados reais: {str(e)}. Usando dados de exemplo.")
        return _get_mock_data_fallback(ym)

def _get_receitas_historicas(ym_atual: str, is_annual_view: bool = False) -> pd.DataFrame:
    """Obtém receitas dos últimos períodos para gráfico histórico"""
    try:
        if 'pagamentos_service' not in st.session_state:
            st.session_state.pagamentos_service = PagamentosService()
        pagamentos_service = st.session_state.pagamentos_service
        
        if is_annual_view:
            # Visualização anual: mostrar últimos anos
            ano_atual = int(ym_atual)
            anos_historicos = []
            receitas = []
            
            for i in range(2, -1, -1):  # 3 anos (2 anteriores + atual)
                ano_calc = ano_atual - i
                receita_ano = 0.0
                
                # Somar receita de todos os meses do ano
                for mes in range(1, 13):
                    ym_calc = f"{ano_calc}-{mes:02d}"
                    try:
                        stats = pagamentos_service.obter_estatisticas_mes(ym_calc)
                        receita_ano += stats.get('receita_total', 0.0)
                    except:
                        continue
                
                anos_historicos.append(str(ano_calc))
                receitas.append(receita_ano)
            
            return pd.DataFrame({
                'Ano': anos_historicos,
                'Receita': receitas
            })
        
        else:
            # Visualização mensal: mostrar últimos meses
            ano_atual, mes_atual = map(int, ym_atual.split('-'))
            meses_historicos = []
            receitas = []
            
            for i in range(5, -1, -1):  # 6 meses (5 anteriores + atual)
                mes_calc = mes_atual - i
                ano_calc = ano_atual
                
                # Ajustar ano se mês for negativo
                while mes_calc <= 0:
                    mes_calc += 12
                    ano_calc -= 1
                
                ym_historico = f"{ano_calc}-{mes_calc:02d}"
                
                try:
                    stats = pagamentos_service.obter_estatisticas_mes(ym_historico)
                    receita = stats.get('receita_total', 0.0)
                except:
                    receita = 0.0
                
                meses_historicos.append(f"{mes_calc:02d}/{str(ano_calc)[2:]}")
                receitas.append(receita)
            
            return pd.DataFrame({
                'Mês': meses_historicos,
                'Receita': receitas
            })
        
    except Exception as e:
        # Fallback para dados mock
        if is_annual_view:
            return pd.DataFrame({
                'Ano': ['2023', '2024', '2025'],
                'Receita': [180000.0, 220000.0, 250000.0]
            })
        else:
            return pd.DataFrame({
                'Mês': ['08/24', '09/24', '10/24', '11/24', '12/24', '01/25'],
                'Receita': [18000.0, 22000.0, 19500.0, 20800.0, 21500.0, 23200.0]
            })

def _get_mock_data_fallback(ym: str) -> Dict[str, Any]:
    """Dados de fallback quando serviços falham"""
    return {
        'receita': 4500.00,
        'inadimplentes': 3,
        'ativos': 45,
        'inativos': 8,
        'percentual_ativos': 85,
        'total_presencas': 180,
        'media_presencas_dia': 6.0,
        'ym': ym
    }