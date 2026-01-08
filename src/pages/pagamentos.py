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
    
    # Menu de navegação - Apenas 2 abas principais
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📋 Lista de Pagamentos", use_container_width=True, 
                    type="primary" if st.session_state.pagamentos_modo == 'lista' else "secondary"):
            st.session_state.pagamentos_modo = 'lista'
            st.rerun()
    
    with col2:
        if st.button("➕ Cadastrar Pagamento", use_container_width=True,
                    type="primary" if st.session_state.pagamentos_modo == 'novo' else "secondary"):
            st.session_state.pagamentos_modo = 'novo'
            st.rerun()
    
    st.markdown("---")
    
    # Renderizar conteúdo baseado no modo
    if st.session_state.pagamentos_modo == 'lista':
        _mostrar_lista_pagamentos_filtrada(pagamentos_service, alunos_service)
    elif st.session_state.pagamentos_modo == 'novo':
        _mostrar_formulario_novo_pagamento(pagamentos_service, alunos_service)
    elif st.session_state.pagamentos_modo == 'editar':
        _mostrar_formulario_editar_pagamento(pagamentos_service, alunos_service)

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
            index=0
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
                index=0
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
        
        mes_selecionado = st.selectbox("📅 Mês:", options=meses_opcoes, index=1 if len(meses_opcoes) > 1 else 0)
        filtro_mes = None if mes_selecionado == "Todos os meses" else mes_selecionado
    
    with col_busca:
        # Busca por nome
        termo_busca = st.text_input(
            "🔍 Buscar aluno:",
            placeholder="Digite o nome...",
            help="Busque por nome do aluno"
        )
    
    # Botão de limpar filtros
    if st.button("🗑️ Limpar Filtros"):
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
        
        # Aplicar filtros no cliente
        pagamentos_filtrados = []
        for pag in pagamentos:
            # Filtro de status
            if filtro_status and pag.get('status') != filtro_status:
                continue
            
            # Filtro de aluno (se tem busca)
            if alunos_ids and pag.get('alunoId') not in alunos_ids:
                continue
            
            # Filtro de turma
            if filtro_turma:
                # Buscar turma do aluno
                aluno = alunos_service.buscar_aluno(pag.get('alunoId'))
                if aluno and aluno.get('turmaId') != filtro_turma:
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
        
        # Mostrar pagamentos em tabela
        for pagamento in pagamentos_filtrados:
            status = pagamento.get('status', 'indefinido')
            ym = pagamento.get('ym', 'N/A')
            aluno_nome = pagamento.get('alunoNome', 'N/A')
            valor = pagamento.get('valor', 0)
            data_vencimento = pagamento.get('dataVencimento', 15)
            
            # Definir cor e emoji por status
            if status == 'pago':
                cor = "🟢"
                status_texto = "Pago"
                cor_fundo = "#d4edda"
            elif status == 'devedor':
                cor = "🔔"
                status_texto = "A Cobrar"
                cor_fundo = "#fff3cd"
            elif status == 'inadimplente':
                cor = "🔴"
                status_texto = "Inadimplente"
                cor_fundo = "#f8d7da"
            elif status == 'ausente':
                cor = "⚪"
                status_texto = "Ausente"
                cor_fundo = "#f8f9fa"
            else:
                cor = "❓"
                status_texto = "Indefinido"
                cor_fundo = "#ffffff"
            
            # Container para cada pagamento
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{cor} {aluno_nome}**")
                
                with col2:
                    st.write(f"📅 {ym}")
                
                with col3:
                    st.write(f"💵 R$ {valor:.2f}")
                    st.caption(f"Venc: dia {data_vencimento:02d}")
                
                with col4:
                    st.write(f"**{status_texto}**")
                
                with col5:
                    if st.button("✏️", key=f"edit_{pagamento.get('id')}", help="Editar"):
                        st.session_state.pagamento_editando = pagamento.get('id')
                        st.session_state.pagamentos_modo = 'editar'
                        st.rerun()
                
                st.divider()
        
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
            modo = st.session_state.get('data_mode', 'operacional')
            min_ano_ref = 2026 if modo == 'operacional' else 2020
            ano_ref = st.number_input("📅 Ano de Referência *", min_value=min_ano_ref, max_value=2030, value=max(hoje.year, min_ano_ref))
        
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

def _mostrar_devedores(pagamentos_service: PagamentosService):
    """Mostra lista de devedores (a cobrar)"""
    
    st.markdown("### 🔔 Lista de Pagamentos A Cobrar")
    st.info("💡 **Devedores:** Alunos que entraram no período de cobrança mas ainda não venceu o prazo (não estão em atraso)")
    
    # Filtro de mês
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Gerar opções de mês/ano
        hoje = date.today()
        modo = st.session_state.get('data_mode', 'operacional')
        min_ym = "2026-01" if modo == 'operacional' else "2024-01"
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

            if mes_ano < min_ym:
                continue

            meses_opcoes.append(mes_ano)
        
        mes_filtro = st.selectbox("📅 Filtrar por mês:", options=meses_opcoes, index=1 if len(meses_opcoes) > 1 else 0)
    
    # Carregar devedores
    try:
        if mes_filtro == "Todos os meses":
            devedores = pagamentos_service.obter_devedores()
        else:
            devedores = pagamentos_service.obter_devedores(ym=mes_filtro)
        
        if not devedores:
            st.success("🎉 Nenhum devedor encontrado! Todos em dia ou já inadimplentes.")
            return
        
        # Exibir devedores
        st.warning(f"🔔 **{len(devedores)} pagamento(s) a cobrar**")
        
        for pagamento in devedores:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**🔔 {pagamento.get('alunoNome', 'N/A')}**")
                    st.markdown(f"📅 Referente a: {pagamento.get('ym', 'N/A')}")
                
                with col2:
                    st.markdown(f"💰 Valor: R$ {pagamento.get('valor', 0):.2f}")
                    
                    # Calcular dias até vencimento
                    try:
                        ano, mes = map(int, pagamento.get('ym', '2024-01').split('-'))
                        dia_vencimento = pagamento.get('dataVencimento', 15)
                        carencia = pagamento.get('carenciaDias', 3)
                        data_vencimento = date(ano, mes, dia_vencimento)
                        data_atraso = data_vencimento + timedelta(days=carencia)
                        dias_ate_atraso = (data_atraso - date.today()).days
                        
                        if dias_ate_atraso > 0:
                            st.markdown(f"⏰ Entra em atraso em {dias_ate_atraso} dia(s)")
                            st.caption(f"Venc: {dia_vencimento:02d} | Carência: {carencia}d")
                        else:
                            st.markdown(f"⏰ Vencido há {abs(dias_ate_atraso)} dia(s)")
                    except:
                        st.markdown("⏰ Calcular vencimento")
                
                with col3:
                    if st.button("💰 Pagar", key=f"pagar_dev_{pagamento.get('id')}", use_container_width=True):
                        if pagamentos_service.marcar_como_pago(pagamento.get('id')):
                            st.success("Pagamento registrado!")
                            st.rerun()
                
                st.markdown("---")
        
        # Resumo financeiro
        valor_total_devedores = sum(p.get('valor', 0) for p in devedores)
        st.warning(f"💰 **Total a cobrar: R$ {valor_total_devedores:.2f}**")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar devedores: {str(e)}")

def _mostrar_inadimplentes(pagamentos_service: PagamentosService):
    """Mostra lista de inadimplentes"""
    
    st.markdown("### 🚫 Lista de Inadimplentes")
    
    # Filtro de mês
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Gerar opções de mês/ano
        hoje = date.today()
        modo = st.session_state.get('data_mode', 'operacional')
        min_ym = "2026-01" if modo == 'operacional' else "2024-01"
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

            if mes_ano < min_ym:
                continue

            meses_opcoes.append(mes_ano)
        
        mes_filtro = st.selectbox("📅 Filtrar por mês:", options=meses_opcoes, index=1 if len(meses_opcoes) > 1 else 0)
    
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

def _mostrar_devedores(pagamentos_service: PagamentosService):
    """Mostra lista de devedores (a cobrar)"""
    
    st.markdown("### 🔔 Lista de Devedores (A Cobrar)")
    st.info("💡 **Devedores** são pagamentos que entraram no período de cobrança mas ainda não venceram. São lembretes para cobrança preventiva.")
    
    # Filtro de mês
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Gerar opções de mês/ano
        hoje = date.today()
        modo = st.session_state.get('data_mode', 'operacional')
        min_ym = "2026-01" if modo == 'operacional' else "2024-01"
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

            if mes_ano < min_ym:
                continue

            meses_opcoes.append(mes_ano)
        
        mes_filtro = st.selectbox("📅 Filtrar por mês:", options=meses_opcoes, index=1 if len(meses_opcoes) > 1 else 0)
    
    # Carregar devedores
    try:
        if mes_filtro == "Todos os meses":
            devedores = pagamentos_service.obter_devedores()
        else:
            devedores = pagamentos_service.obter_devedores(ym=mes_filtro)
        
        if not devedores:
            st.success("🎉 Nenhum devedor encontrado! Todos em dia ou já inadimplentes.")
            return
        
        # Exibir devedores
        st.warning(f"🔔 **{len(devedores)} pagamento(s) a cobrar**")
        
        for pagamento in devedores:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**🔔 {pagamento.get('alunoNome', 'N/A')}**")
                    st.markdown(f"📅 Referente a: {pagamento.get('ym', 'N/A')}")
                
                with col2:
                    st.markdown(f"💰 Valor: R$ {pagamento.get('valor', 0):.2f}")
                    
                    # Mostrar dia de vencimento e carência
                    vencimento = pagamento.get('dataVencimento', 15)
                    carencia = pagamento.get('carenciaDias', 3)
                    st.markdown(f"📅 Vencimento: dia {vencimento:02d} (+ {carencia} dias)")
                    
                    # Calcular quando vira inadimplente
                    try:
                        ano, mes = map(int, pagamento.get('ym', '2024-01').split('-'))
                        data_vencimento = date(ano, mes, vencimento)
                        data_inadimplencia = data_vencimento + timedelta(days=carencia)
                        dias_restantes = (data_inadimplencia - date.today()).days
                        
                        if dias_restantes > 0:
                            st.caption(f"⏰ {dias_restantes} dias até vencer")
                        else:
                            st.caption(f"⏰ Venceu há {abs(dias_restantes)} dias")
                    except:
                        st.caption("⏰ Verificar vencimento")
                
                with col3:
                    if st.button("💰 Pagar", key=f"pagar_dev_{pagamento.get('id')}", use_container_width=True):
                        if pagamentos_service.marcar_como_pago(pagamento.get('id')):
                            st.success("Pagamento registrado!")
                            st.rerun()
                
                st.markdown("---")
        
        # Resumo financeiro
        valor_total_devedores = sum(p.get('valor', 0) for p in devedores)
        st.warning(f"💰 **Total a cobrar: R$ {valor_total_devedores:.2f}**")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar devedores: {str(e)}")

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
            
            st.bar_chart(chart_data.set_index('Status')['Quantidade'])
        
        with col2:
            st.markdown("#### 💵 Valores por Status")
            st.bar_chart(chart_data.set_index('Status')['Valor'])
        
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