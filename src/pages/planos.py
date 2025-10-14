"""
Página de Planos - CRUD e gerenciamento completo
Integrado ao PlanosService
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, List
from src.services.planos_service import PlanosService

def show_planos():
    """Exibe a página de gerenciamento de planos"""
    
    # Inicializar serviço de planos
    if 'planos_service' not in st.session_state:
        try:
            st.session_state.planos_service = PlanosService()
        except Exception as e:
            st.error(f"❌ Erro ao conectar com o banco de dados: {str(e)}")
            return
    
    planos_service = st.session_state.planos_service
    
    st.markdown("## 💰 Gerenciamento de Planos")
    
    # Controle de aba/modo
    if 'planos_modo' not in st.session_state:
        st.session_state.planos_modo = 'lista'
    
    # Menu de navegação
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📋 Lista de Planos", use_container_width=True, 
                    type="primary" if st.session_state.planos_modo == 'lista' else "secondary"):
            st.session_state.planos_modo = 'lista'
            st.rerun()
    
    with col2:
        if st.button("➕ Novo Plano", use_container_width=True,
                    type="primary" if st.session_state.planos_modo == 'novo' else "secondary"):
            st.session_state.planos_modo = 'novo'
            st.rerun()
    
    with col3:
        if st.button("📊 Estatísticas", use_container_width=True,
                    type="primary" if st.session_state.planos_modo == 'stats' else "secondary"):
            st.session_state.planos_modo = 'stats'
            st.rerun()
    
    st.markdown("---")
    
    # Renderizar conteúdo baseado no modo
    if st.session_state.planos_modo == 'lista':
        _mostrar_lista_planos(planos_service)
    elif st.session_state.planos_modo == 'novo':
        _mostrar_formulario_novo_plano(planos_service)
    elif st.session_state.planos_modo == 'editar':
        _mostrar_formulario_editar_plano(planos_service)
    elif st.session_state.planos_modo == 'stats':
        _mostrar_estatisticas_planos(planos_service)

def _mostrar_lista_planos(planos_service: PlanosService):
    """Mostra a lista de planos com filtros"""
    
    st.markdown("### 📋 Lista de Planos")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_status = st.selectbox(
            "🎯 Filtrar por Status:",
            options=["Todos", "Ativo", "Inativo"],
            index=0
        )
    
    with col2:
        ordenar_por = st.selectbox(
            "📊 Ordenar por:",
            options=["nome", "valor", "ativo"],
            index=0
        )
    
    # Carregar e filtrar planos
    try:
        if filtro_status == "Todos":
            planos = planos_service.listar_planos(apenas_ativos=None, ordenar_por=ordenar_por)
        else:
            apenas_ativos = filtro_status == "Ativo"
            planos = planos_service.listar_planos(apenas_ativos=apenas_ativos, ordenar_por=ordenar_por)
        
        if not planos:
            st.info("📭 Nenhum plano encontrado. Cadastre o primeiro plano!")
            return
        
        # Preparar dados para exibição
        dados_tabela = []
        for plano in planos:
            # Formatar status com emoji
            status_emoji = "✅" if plano.get('ativo', False) else "⏸️"
            status_texto = f"{status_emoji} {'Ativo' if plano.get('ativo', False) else 'Inativo'}"
            
            # Formatar valor
            valor_formatado = f"R$ {plano.get('valor', 0):.2f}"
            
            dados_tabela.append({
                'Nome': plano.get('nome', ''),
                'Status': status_texto,
                'Valor': valor_formatado,
                'Periodicidade': plano.get('periodicidade', 'mensal').title(),
                'Dia Padrão': plano.get('diaPadraoVencimento', 'N/A'),
                'ID': plano.get('id', '')
            })
        
        # Exibir tabela
        df = pd.DataFrame(dados_tabela)
        
        # Configurar exibição das colunas
        column_config = {
            "ID": None,  # Esconder ID
            "Nome": st.column_config.TextColumn("💰 Nome", width="large"),
            "Status": st.column_config.TextColumn("📊 Status", width="medium"),
            "Valor": st.column_config.TextColumn("💵 Valor", width="medium"),
            "Periodicidade": st.column_config.TextColumn("📅 Periodicidade", width="medium"),
            "Dia Padrão": st.column_config.TextColumn("📆 Dia Padrão", width="small")
        }
        
        # Mostrar dataframe interativo
        evento = st.dataframe(
            df,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Ações para linha selecionada
        if evento.selection.rows:
            linha_selecionada = evento.selection.rows[0]
            plano_selecionado = dados_tabela[linha_selecionada]
            
            st.markdown("---")
            st.markdown(f"### 🎯 Plano Selecionado: **{plano_selecionado['Nome']}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Editar", use_container_width=True):
                    st.session_state.plano_editando = plano_selecionado['ID']
                    st.session_state.planos_modo = 'editar'
                    st.rerun()
            
            with col2:
                if plano_selecionado['Status'].startswith('✅'):
                    if st.button("⏸️ Inativar", use_container_width=True):
                        if planos_service.inativar_plano(plano_selecionado['ID']):
                            st.success("✅ Plano inativado!")
                            st.rerun()
                else:
                    if st.button("▶️ Ativar", use_container_width=True):
                        if planos_service.ativar_plano(plano_selecionado['ID']):
                            st.success("✅ Plano ativado!")
                            st.rerun()
            
            with col3:
                if st.button("👁️ Detalhes", use_container_width=True):
                    _mostrar_detalhes_plano(planos_service, plano_selecionado['ID'])
            
            with col4:
                if st.button("👥 Alunos", use_container_width=True):
                    st.info("🚧 Lista de alunos por plano em desenvolvimento...")
        
        # Resumo
        st.markdown("---")
        st.markdown(f"**📊 Total: {len(planos)} plano(s) encontrado(s)**")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar planos: {str(e)}")

def _mostrar_formulario_novo_plano(planos_service: PlanosService):
    """Mostra formulário para cadastrar novo plano"""
    
    st.markdown("### ➕ Cadastrar Novo Plano")
    
    # Mostrar sucesso se plano foi cadastrado
    if 'plano_cadastrado' in st.session_state:
        plano_info = st.session_state.plano_cadastrado
        st.success(f"✅ Plano **{plano_info['nome']}** cadastrado com sucesso!")
        st.info(f"🆔 ID: {plano_info['id']}")
        st.info(f"💰 Valor: R$ {plano_info['valor']:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Ver na Lista", type="primary", use_container_width=True):
                del st.session_state.plano_cadastrado
                st.session_state.planos_modo = 'lista'
                st.rerun()
        
        with col2:
            if st.button("➕ Cadastrar Outro", type="secondary", use_container_width=True):
                del st.session_state.plano_cadastrado
                st.rerun()
        
        st.markdown("---")
    
    with st.form("form_novo_plano", clear_on_submit=True):
        # Dados básicos
        st.markdown("#### 📝 Dados Básicos")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("💰 Nome do Plano *", placeholder="Ex: Plano Básico, Premium, etc.")
            valor = st.number_input("💵 Valor Mensal (R$) *", min_value=0.01, step=0.01, format="%.2f")
        
        with col2:
            ativo = st.selectbox("📊 Status *", options=[True, False], 
                               format_func=lambda x: "Ativo" if x else "Inativo", index=0)
            dia_padrao = st.number_input("📆 Dia Padrão Vencimento", min_value=1, max_value=28, 
                                       value=15, help="Dia do mês para vencimento padrão (1-28)")
        
        # Informações adicionais
        st.markdown("#### ℹ️ Informações")
        st.info("📅 **Periodicidade:** Mensal (fixo no MVP)")
        
        # Botões
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("✅ Cadastrar", type="primary", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🔄 Limpar", use_container_width=True):
                st.rerun()
        
        # Processar formulário
        if submitted:
            # Validações
            if not nome or not nome.strip():
                st.error("❌ Nome é obrigatório!")
                return
            
            if valor <= 0:
                st.error("❌ Valor deve ser maior que zero!")
                return
            
            # Preparar dados
            dados_plano = {
                'nome': nome.strip(),
                'valor': valor,
                'ativo': ativo,
                'diaPadraoVencimento': dia_padrao
            }
            
            # Cadastrar plano
            try:
                plano_id = planos_service.criar_plano(dados_plano)
                st.session_state.plano_cadastrado = {
                    'nome': nome,
                    'id': plano_id,
                    'valor': valor
                }
                st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar plano: {str(e)}")

def _mostrar_formulario_editar_plano(planos_service: PlanosService):
    """Mostra formulário para editar plano existente"""
    
    # Verificar se tem plano para editar
    if 'plano_editando' not in st.session_state or not st.session_state.plano_editando:
        st.error("❌ Nenhum plano selecionado para edição!")
        if st.button("📋 Voltar para Lista"):
            st.session_state.planos_modo = 'lista'
            st.rerun()
        return
    
    plano_id = st.session_state.plano_editando
    
    try:
        # Carregar dados do plano
        plano = planos_service.buscar_plano(plano_id)
        
        if not plano:
            st.error("❌ Plano não encontrado!")
            if st.button("📋 Voltar para Lista"):
                st.session_state.planos_modo = 'lista'
                st.rerun()
            return
        
        st.markdown(f"### ✏️ Editar Plano: **{plano.get('nome', 'N/A')}**")
        
        # Botão voltar
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔙 Voltar para Lista", type="secondary"):
                st.session_state.planos_modo = 'lista'
                del st.session_state.plano_editando
                st.rerun()
        
        with st.form("form_editar_plano", clear_on_submit=False):
            # Dados básicos
            st.markdown("#### 📝 Dados Básicos")
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input(
                    "💰 Nome do Plano *", 
                    value=plano.get('nome', ''),
                    placeholder="Ex: Plano Básico, Premium, etc."
                )
                valor = st.number_input(
                    "💵 Valor Mensal (R$) *", 
                    min_value=0.01, 
                    step=0.01, 
                    format="%.2f",
                    value=float(plano.get('valor', 0))
                )
            
            with col2:
                ativo = st.selectbox(
                    "📊 Status *", 
                    options=[True, False], 
                    format_func=lambda x: "Ativo" if x else "Inativo",
                    index=0 if plano.get('ativo', True) else 1
                )
                dia_padrao = st.number_input(
                    "📆 Dia Padrão Vencimento", 
                    min_value=1, 
                    max_value=28, 
                    value=int(plano.get('diaPadraoVencimento', 15)),
                    help="Dia do mês para vencimento padrão (1-28)"
                )
            
            # Informações adicionais
            st.markdown("#### ℹ️ Informações")
            st.info("📅 **Periodicidade:** Mensal (fixo no MVP)")
            
            # Botões
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submitted = st.form_submit_button("✅ Salvar Alterações", type="primary", use_container_width=True)
            
            with col2:
                if st.form_submit_button("🔄 Restaurar", use_container_width=True):
                    st.rerun()
            
            # Processar formulário
            if submitted:
                # Validações
                if not nome or not nome.strip():
                    st.error("❌ Nome é obrigatório!")
                    return
                
                if valor <= 0:
                    st.error("❌ Valor deve ser maior que zero!")
                    return
                
                # Preparar dados de atualização
                dados_atualizacao = {
                    'nome': nome.strip(),
                    'valor': valor,
                    'ativo': ativo,
                    'diaPadraoVencimento': dia_padrao
                }
                
                # Atualizar plano
                try:
                    sucesso = planos_service.atualizar_plano(plano_id, dados_atualizacao)
                    
                    if sucesso:
                        st.success(f"✅ Plano **{nome}** atualizado com sucesso!")
                        # Marcar para mostrar opções pós-edição fora do form
                        st.session_state.plano_atualizado = True
                        
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar plano: {str(e)}")
        
        # Opções pós-edição (FORA do formulário)
        if st.session_state.get('plano_atualizado', False):
            st.markdown("---")
            st.markdown("### 🎉 Opções Pós-Edição")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Voltar para Lista", type="secondary"):
                    st.session_state.planos_modo = 'lista'
                    if 'plano_editando' in st.session_state:
                        del st.session_state.plano_editando
                    st.session_state.plano_atualizado = False
                    st.rerun()
            
            with col2:
                if st.button("👁️ Ver Detalhes", type="secondary"):
                    st.session_state.plano_detalhes = plano_id
                    st.session_state.planos_modo = 'detalhes'
                    st.session_state.plano_atualizado = False
                    st.rerun()
            
            with col3:
                if st.button("✏️ Continuar Editando", type="secondary"):
                    st.session_state.plano_atualizado = False
                    st.rerun()
        
        # Ações rápidas adicionais
        st.markdown("---")
        st.markdown("#### ⚡ Ações Rápidas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if plano.get('ativo', False):
                if st.button("⏸️ Inativar Plano", use_container_width=True):
                    if planos_service.inativar_plano(plano_id):
                        st.success("✅ Plano inativado!")
                        st.rerun()
            else:
                if st.button("▶️ Ativar Plano", use_container_width=True):
                    if planos_service.ativar_plano(plano_id):
                        st.success("✅ Plano ativado!")
                        st.rerun()
        
        with col2:
            if st.button("👁️ Ver Detalhes Completos", use_container_width=True):
                with st.expander("📄 Detalhes Completos", expanded=True):
                    _mostrar_detalhes_plano(planos_service, plano_id)
        
        with col3:
            if st.button("👥 Alunos deste Plano", use_container_width=True):
                st.info("🚧 Lista de alunos por plano em desenvolvimento...")
        
        with col4:
            if st.button("💰 Relatório Financeiro", use_container_width=True):
                st.info("🚧 Relatórios em desenvolvimento...")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar plano para edição: {str(e)}")
        if st.button("📋 Voltar para Lista"):
            st.session_state.planos_modo = 'lista'
            if 'plano_editando' in st.session_state:
                del st.session_state.plano_editando
            st.rerun()

def _mostrar_estatisticas_planos(planos_service: PlanosService):
    """Mostra estatísticas dos planos"""
    
    st.markdown("### 📊 Estatísticas dos Planos")
    
    try:
        stats = planos_service.obter_estatisticas()
        
        # Cards de estatísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total de Planos",
                value=stats['total'],
                help="Total de planos cadastrados"
            )
        
        with col2:
            st.metric(
                label="✅ Planos Ativos",
                value=stats['ativos'],
                delta=f"{(stats['ativos']/stats['total']*100):.1f}%" if stats['total'] > 0 else "0%",
                help="Planos com status ativo"
            )
        
        with col3:
            st.metric(
                label="⏸️ Planos Inativos",
                value=stats['inativos'],
                delta=f"{(stats['inativos']/stats['total']*100):.1f}%" if stats['total'] > 0 else "0%",
                help="Planos com status inativo"
            )
        
        with col4:
            st.metric(
                label="💵 Valor Médio",
                value=f"R$ {stats['valor_medio']:.2f}",
                help="Valor médio dos planos ativos"
            )
        
        # Análise de valores
        if stats['ativos'] > 0:
            st.markdown("---")
            st.markdown("#### 💰 Análise de Valores")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📊 Faixa de Valores")
                st.metric("💵 Menor Valor", f"R$ {stats['valor_min']:.2f}")
                st.metric("💰 Maior Valor", f"R$ {stats['valor_max']:.2f}")
                st.metric("📈 Diferença", f"R$ {stats['valor_max'] - stats['valor_min']:.2f}")
            
            with col2:
                st.markdown("##### 📈 Distribuição por Faixa de Preço")
                
                # Preparar dados para gráfico
                faixas_df = pd.DataFrame(
                    list(stats['faixas_preco'].items()),
                    columns=['Faixa', 'Quantidade']
                )
                
                # Gráfico de barras
                st.bar_chart(faixas_df.set_index('Faixa'))
        
        # Tabela detalhada das faixas
        if stats['faixas_preco']:
            st.markdown("---")
            st.markdown("#### 📋 Detalhes por Faixa de Preço")
            
            faixas_df = pd.DataFrame(
                list(stats['faixas_preco'].items()),
                columns=['Faixa de Preço', 'Quantidade de Planos']
            )
            
            st.dataframe(
                faixas_df,
                column_config={
                    "Faixa de Preço": "💰 Faixa de Preço",
                    "Quantidade de Planos": "📊 Quantidade"
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Dicas e insights
        st.markdown("---")
        st.markdown("#### 💡 Insights")
        
        if stats['total'] > 0:
            planos_ativos = planos_service.listar_planos(apenas_ativos=True)
            
            if planos_ativos:
                plano_mais_caro = max(planos_ativos, key=lambda x: x.get('valor', 0))
                plano_mais_barato = min(planos_ativos, key=lambda x: x.get('valor', 0))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"💎 **Plano mais caro:** {plano_mais_caro.get('nome')} - R$ {plano_mais_caro.get('valor', 0):.2f}")
                
                with col2:
                    st.info(f"💰 **Plano mais acessível:** {plano_mais_barato.get('nome')} - R$ {plano_mais_barato.get('valor', 0):.2f}")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar estatísticas: {str(e)}")

def _mostrar_detalhes_plano(planos_service: PlanosService, plano_id: str):
    """Mostra detalhes completos de um plano"""
    
    try:
        plano = planos_service.buscar_plano(plano_id)
        
        if not plano:
            st.error("❌ Plano não encontrado!")
            return
        
        st.markdown(f"### 💰 Detalhes: **{plano.get('nome', 'N/A')}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Dados Básicos")
            st.write(f"**ID:** {plano.get('id', 'N/A')}")
            st.write(f"**Status:** {'Ativo' if plano.get('ativo', False) else 'Inativo'}")
            st.write(f"**Valor:** R$ {plano.get('valor', 0):.2f}")
            st.write(f"**Periodicidade:** {plano.get('periodicidade', 'mensal').title()}")
        
        with col2:
            st.markdown("#### ⚙️ Configurações")
            st.write(f"**Dia Padrão Vencimento:** {plano.get('diaPadraoVencimento', 'N/A')}")
            if plano.get('createdAt'):
                st.write(f"**Criado em:** {plano.get('createdAt')}")
            if plano.get('updatedAt'):
                st.write(f"**Atualizado em:** {plano.get('updatedAt')}")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar detalhes: {str(e)}")