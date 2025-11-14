"""
Página de Alunos - CRUD e gerenciamento completo
Integrado ao AlunosService
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, List
from src.services.alunos_service import AlunosService
from src.services.graduacoes_service import GraduacoesService
from src.services.turmas_service import TurmasService

def show_alunos():
    """Exibe a página de gerenciamento de alunos"""
    
    # Inicializar serviço de alunos
    if 'alunos_service' not in st.session_state:
        try:
            st.session_state.alunos_service = AlunosService()
        except Exception as e:
            st.error(f"❌ Erro ao conectar com o banco de dados: {str(e)}")
            return
    
    alunos_service = st.session_state.alunos_service
    
    st.markdown("## 👥 Gerenciamento de Alunos")
    
    # Controle de aba/modo
    if 'alunos_modo' not in st.session_state:
        st.session_state.alunos_modo = 'lista'
    
    # Menu de navegação
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("📋 Lista de Alunos", use_container_width=True, 
                    type="primary" if st.session_state.alunos_modo == 'lista' else "secondary"):
            st.session_state.alunos_modo = 'lista'
            st.rerun()
    
    with col2:
        if st.button("➕ Novo Aluno", use_container_width=True,
                    type="primary" if st.session_state.alunos_modo == 'novo' else "secondary"):
            st.session_state.alunos_modo = 'novo'
            st.rerun()
    
    with col3:
        if st.button("� Buscar", use_container_width=True,
                    type="primary" if st.session_state.alunos_modo == 'buscar' else "secondary"):
            st.session_state.alunos_modo = 'buscar'
            st.rerun()
    
    with col4:
        if st.button("📊 Estatísticas", use_container_width=True,
                    type="primary" if st.session_state.alunos_modo == 'stats' else "secondary"):
            st.session_state.alunos_modo = 'stats'
            st.rerun()
    
    st.markdown("---")
    
    # Renderizar conteúdo baseado no modo
    if st.session_state.alunos_modo == 'lista':
        _mostrar_lista_alunos(alunos_service)
    elif st.session_state.alunos_modo == 'novo':
        _mostrar_formulario_novo_aluno(alunos_service)
    elif st.session_state.alunos_modo == 'editar':
        _mostrar_formulario_editar_aluno(alunos_service)
    elif st.session_state.alunos_modo == 'buscar':
        _mostrar_busca_alunos(alunos_service)
    elif st.session_state.alunos_modo == 'stats':
        _mostrar_estatisticas_alunos(alunos_service)

def _mostrar_lista_alunos(alunos_service: AlunosService):
    """Mostra a lista de alunos com filtros"""
    
    st.markdown("### 📋 Lista de Alunos")
    
    # Inicializar serviço de graduações
    if 'graduacoes_service' not in st.session_state:
        try:
            st.session_state.graduacoes_service = GraduacoesService()
        except Exception as e:
            st.warning(f"⚠️ Serviço de graduações indisponível: {str(e)}")
            st.session_state.graduacoes_service = None
    
    graduacoes_service = st.session_state.graduacoes_service
    
    # Buscar turmas disponíveis primeiro (para definir opções antes dos filtros)
    try:
        todos_alunos = alunos_service.listar_alunos()
        turmas_disponiveis = sorted(list(set([a.get('turma', '') for a in todos_alunos if a.get('turma')])))
        # Reorganizar: turmas específicas primeiro, "Todas" por último
        turmas_opcoes = turmas_disponiveis + ["Todas"]
    except:
        turmas_opcoes = ["KIDS", "Todas"]
    
    # Inicializar estado dos filtros se não existir
    if 'filtro_turma_alunos' not in st.session_state:
        # Definir KIDS como padrão se existir, senão primeira turma
        if "KIDS" in turmas_opcoes:
            st.session_state.filtro_turma_alunos = turmas_opcoes.index("KIDS")
        else:
            st.session_state.filtro_turma_alunos = 0
    
    if 'filtro_status_alunos' not in st.session_state:
        st.session_state.filtro_status_alunos = 0
    if 'filtro_vencimento_alunos' not in st.session_state:
        st.session_state.filtro_vencimento_alunos = 0
    if 'ordenar_por_alunos' not in st.session_state:
        st.session_state.ordenar_por_alunos = 0
    
    # Buscar vencimentos disponíveis
    try:
        vencimentos_disponiveis = sorted(list(set([a.get('vencimentoDia') for a in todos_alunos if a.get('vencimentoDia')])))
        vencimentos_opcoes = ["Todos"] + [str(v) for v in vencimentos_disponiveis]
    except:
        vencimentos_opcoes = ["Todos"]
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Turma como primeiro filtro (mais importante para performance)
        filtro_turma_idx = st.session_state.filtro_turma_alunos
        filtro_turma = st.selectbox(
            "👥 Turma:",
            options=turmas_opcoes,
            index=filtro_turma_idx,
            help="Filtre por turma específica para melhor performance. 'Todas' carrega todos os alunos."
        )
        # Atualizar session_state apenas se mudou
        novo_idx = turmas_opcoes.index(filtro_turma)
        if novo_idx != st.session_state.filtro_turma_alunos:
            st.session_state.filtro_turma_alunos = novo_idx
    
    with col2:
        status_opcoes = ["Todos", "Ativo", "Inativo"]
        filtro_status_idx = st.session_state.filtro_status_alunos
        filtro_status = st.selectbox(
            "🎯 Status:",
            options=status_opcoes,
            index=filtro_status_idx
        )
        # Atualizar session_state apenas se mudou
        novo_idx = status_opcoes.index(filtro_status)
        if novo_idx != st.session_state.filtro_status_alunos:
            st.session_state.filtro_status_alunos = novo_idx
    
    with col3:
        filtro_vencimento_idx = st.session_state.filtro_vencimento_alunos
        filtro_vencimento = st.selectbox(
            "📅 Vencimento:",
            options=vencimentos_opcoes,
            index=filtro_vencimento_idx
        )
        # Atualizar session_state apenas se mudou
        novo_idx = vencimentos_opcoes.index(filtro_vencimento)
        if novo_idx != st.session_state.filtro_vencimento_alunos:
            st.session_state.filtro_vencimento_alunos = novo_idx
    
    with col4:
        ordenar_opcoes = ["nome", "status", "vencimentoDia", "ativoDesde", "turma"]
        ordenar_idx = st.session_state.ordenar_por_alunos
        ordenar_por = st.selectbox(
            "📊 Ordenar:",
            options=ordenar_opcoes,
            index=ordenar_idx,
            format_func=lambda x: {
                "nome": "Nome",
                "status": "Status",
                "vencimentoDia": "Vencimento",
                "ativoDesde": "Data Cadastro",
                "turma": "Turma"
            }.get(x, x)
        )
        # Atualizar session_state apenas se mudou
        novo_idx = ordenar_opcoes.index(ordenar_por)
        if novo_idx != st.session_state.ordenar_por_alunos:
            st.session_state.ordenar_por_alunos = novo_idx
    
    # Botão Limpar Filtros
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("🔄 Limpar Filtros", use_container_width=True):
            # Resetar todos os filtros para valores padrão
            # TURMA -> KIDS (se existir, senão primeira opção)
            if "KIDS" in turmas_opcoes:
                st.session_state.filtro_turma_alunos = turmas_opcoes.index("KIDS")
            else:
                st.session_state.filtro_turma_alunos = 0
            
            # STATUS -> Todos (índice 0 em ["Todos", "Ativo", "Inativo"])
            st.session_state.filtro_status_alunos = 0
            
            # VENCIMENTO -> Todos (índice 0 em ["Todos", ...])
            st.session_state.filtro_vencimento_alunos = 0
            
            # ORDENAR -> nome (índice 0 em ["nome", "status", "vencimentoDia", "ativoDesde", "turma"])
            st.session_state.ordenar_por_alunos = 0
            
            st.rerun()
    
    st.markdown("---")
    
    # Carregar e filtrar alunos - OTIMIZADO
    try:
        # Se uma turma específica foi selecionada (não "Todas"), carregar apenas essa turma
        if filtro_turma != "Todas":
            # Carregar todos os alunos primeiro (necessário para o filtro por turma)
            status_filtro = None if filtro_status == "Todos" else filtro_status.lower()
            alunos = alunos_service.listar_alunos(status=status_filtro, ordenar_por=ordenar_por)
            # Filtrar por turma específica
            alunos = [a for a in alunos if a.get('turma') == filtro_turma]
        else:
            # Carregar todos os alunos
            status_filtro = None if filtro_status == "Todos" else filtro_status.lower()
            alunos = alunos_service.listar_alunos(status=status_filtro, ordenar_por=ordenar_por)
        
        # Aplicar filtro de vencimento
        if filtro_vencimento != "Todos":
            vencimento_num = int(filtro_vencimento)
            alunos = [a for a in alunos if a.get('vencimentoDia') == vencimento_num]
        
        if not alunos:
            st.info(f"📭 Nenhum aluno encontrado na turma **{filtro_turma}**.")
            return
        
        # Mostrar informação de quantos alunos foram carregados
        total_alunos = len(alunos)
        if filtro_turma != "Todas":
            st.info(f"👥 **{total_alunos}** aluno(s) encontrado(s) na turma **{filtro_turma}**")
        else:
            st.info(f"👥 **{total_alunos}** aluno(s) no total (todas as turmas)")
        
        # Preparar dados para exibição
        dados_tabela = []
        for aluno in alunos:
            # Formatar status com emoji
            status_emoji = "✅" if aluno.get('status') == 'ativo' else "⏸️"
            status_texto = f"{status_emoji} {aluno.get('status', '').title()}"
            
            # Formatar contato
            contato = aluno.get('contato', {})
            telefone = contato.get('telefone', 'N/A') if isinstance(contato, dict) else 'N/A'
            
            # Obter graduação atual e histórico
            graduacao_atual = aluno.get('graduacao', 'Sem graduação')
            graduacao_tooltip = graduacao_atual
            
            # Buscar histórico de graduações se disponível
            if graduacoes_service and aluno.get('id'):
                try:
                    historico = graduacoes_service.listar_graduacoes_aluno(aluno.get('id'))
                    if historico:
                        # Criar tooltip com histórico
                        historico_texto = []
                        for idx, grad in enumerate(reversed(historico[-5:])):  # Últimas 5 graduações
                            data_grad = grad.get('data', 'N/A')
                            nivel_grad = grad.get('nivel', 'N/A')
                            historico_texto.append(f"{idx+1}. {nivel_grad} ({data_grad})")
                        
                        if historico_texto:
                            graduacao_tooltip = "Histórico:\n" + "\n".join(historico_texto)
                except Exception:
                    pass  # Silenciosamente falhar se não conseguir buscar
            
            dados_tabela.append({
                'Nome': aluno.get('nome', ''),
                'Graduação': graduacao_atual,
                'Graduação_Tooltip': graduacao_tooltip,
                'Status': status_texto,
                'Vencimento': f"Dia {aluno.get('vencimentoDia', 'N/A')}",
                'Telefone': telefone,
                'Turma': aluno.get('turma', 'N/A'),
                'Ativo Desde': aluno.get('ativoDesde', 'N/A'),
                'ID': aluno.get('id', '')
            })
        
        # Exibir tabela
        df = pd.DataFrame(dados_tabela)
        
        # Configurar exibição das colunas
        column_config = {
            "ID": None,  # Esconder ID
            "Graduação_Tooltip": None,  # Esconder coluna de tooltip
            "Nome": st.column_config.TextColumn("👤 Nome", width="large"),
            "Graduação": st.column_config.TextColumn(
                "🥋 Graduação", 
                width="medium",
                help="Graduação atual do aluno. Selecione a linha para ver histórico completo."
            ),
            "Status": st.column_config.TextColumn("📊 Status", width="small"),
            "Vencimento": st.column_config.TextColumn("📅 Venc.", width="small"),
            "Telefone": st.column_config.TextColumn("📞 Telefone", width="medium"),
            "Turma": st.column_config.TextColumn("👥 Turma", width="small"),
            "Ativo Desde": st.column_config.TextColumn("📆 Desde", width="small")
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
            aluno_selecionado = dados_tabela[linha_selecionada]
            
            st.markdown("---")
            st.markdown(f"### 🎯 Aluno Selecionado: **{aluno_selecionado['Nome']}**")
            
            # Exibir histórico de graduações do aluno selecionado
            if graduacoes_service and aluno_selecionado['Graduação_Tooltip'].startswith('Histórico:'):
                with st.expander("🎓 Histórico de Graduações", expanded=False):
                    try:
                        historico = graduacoes_service.listar_graduacoes_aluno(aluno_selecionado['ID'])
                        if historico:
                            st.markdown(f"**Graduação Atual:** {aluno_selecionado['Graduação']}")
                            st.markdown("**Histórico completo:**")
                            
                            for idx, grad in enumerate(reversed(historico), 1):
                                data_grad = grad.get('data', 'N/A')
                                nivel_grad = grad.get('nivel', 'N/A')
                                obs_grad = grad.get('obs', '')
                                
                                if obs_grad:
                                    st.markdown(f"{idx}. **{nivel_grad}** - {data_grad} _{obs_grad}_")
                                else:
                                    st.markdown(f"{idx}. **{nivel_grad}** - {data_grad}")
                        else:
                            st.info("Nenhuma graduação registrada ainda.")
                    except Exception as e:
                        st.error(f"Erro ao carregar histórico: {str(e)}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Editar", use_container_width=True):
                    st.session_state.aluno_editando = aluno_selecionado['ID']
                    st.session_state.alunos_modo = 'editar'
                    st.rerun()
            
            with col2:
                if aluno_selecionado['Status'].startswith('✅'):
                    if st.button("⏸️ Inativar", use_container_width=True):
                        if alunos_service.inativar_aluno(aluno_selecionado['ID']):
                            st.success("✅ Aluno inativado!")
                            st.rerun()
                else:
                    if st.button("▶️ Reativar", use_container_width=True):
                        if alunos_service.reativar_aluno(aluno_selecionado['ID']):
                            st.success("✅ Aluno reativado!")
                            st.rerun()
            
            with col3:
                if st.button("👁️ Detalhes", use_container_width=True):
                    _mostrar_detalhes_aluno(alunos_service, aluno_selecionado['ID'])
            
            with col4:
                if st.button("🎓 Graduações", use_container_width=True):
                    st.info("🚧 Graduações em desenvolvimento...")
        
        # Resumo
        st.markdown("---")
        st.markdown(f"**📊 Total: {len(alunos)} aluno(s) encontrado(s)**")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar alunos: {str(e)}")

def _mostrar_formulario_novo_aluno(alunos_service: AlunosService):
    """Mostra formulário para cadastrar novo aluno"""
    
    st.markdown("### ➕ Cadastrar Novo Aluno")
    
    # Mostrar sucesso se aluno foi cadastrado
    if 'aluno_cadastrado' in st.session_state:
        aluno_info = st.session_state.aluno_cadastrado
        st.success(f"✅ Aluno **{aluno_info['nome']}** cadastrado com sucesso!")
        st.info(f"🆔 ID: {aluno_info['id']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Ver na Lista", type="primary", use_container_width=True):
                del st.session_state.aluno_cadastrado
                st.session_state.alunos_modo = 'lista'
                st.rerun()
        
        with col2:
            if st.button("➕ Cadastrar Outro", type="secondary", use_container_width=True):
                del st.session_state.aluno_cadastrado
                st.rerun()
        
        st.markdown("---")
    
    with st.form("form_novo_aluno", clear_on_submit=True):
        # Dados básicos
        st.markdown("#### 📝 Dados Básicos")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("👤 Nome Completo *", placeholder="Digite o nome completo")
            vencimento_dia = st.selectbox(
                "📅 Dia do Vencimento *", 
                options=[10, 15, 25],
                index=1  # 15 como padrão
            )
        
        with col2:
            status = st.selectbox("📊 Status *", options=["ativo", "inativo"], index=0)
            ativo_desde = st.date_input(
                "📆 Ativo Desde *", 
                value=date.today(),
                min_value=date(2024, 1, 1),
                max_value=date.today(),
                help="Data de início na academia (entre 01/01/2024 e hoje)"
            )
        
        # Contato
        st.markdown("#### 📞 Contato")
        col1, col2 = st.columns(2)
        
        with col1:
            telefone = st.text_input("📱 Telefone", placeholder="(11) 99999-9999")
        
        with col2:
            email = st.text_input("📧 Email", placeholder="aluno@email.com")
        
        # Outros dados
        st.markdown("#### 🏠 Dados Adicionais")
        col1, col2 = st.columns(2)
        
        with col1:
            endereco = st.text_input("🏠 Endereço", placeholder="Rua, número, bairro")
        
        with col2:
            # Buscar turmas do banco de dados
            try:
                if 'turmas_service' not in st.session_state:
                    st.session_state.turmas_service = TurmasService()
                
                turmas_service = st.session_state.turmas_service
                turmas_db = turmas_service.listar_turmas(apenas_ativas=True)
                
                if turmas_db:
                    # Usar turmas do banco
                    turmas_opcoes = [f"{t['nome']} ({t['horarioInicio']} às {t['horarioFim']})" for t in turmas_db]
                    turmas_nomes = [t['nome'] for t in turmas_db]
                else:
                    # Fallback se não houver turmas cadastradas
                    turmas_opcoes = ["⚠️ Nenhuma turma cadastrada"]
                    turmas_nomes = []
                    st.warning("⚠️ Nenhuma turma cadastrada. Por favor, cadastre turmas primeiro na página de Turmas.")
                
            except Exception as e:
                st.error(f"Erro ao carregar turmas: {str(e)}")
                turmas_opcoes = ["⚠️ Erro ao carregar turmas"]
                turmas_nomes = []
            
            if turmas_nomes:
                turma_selecionada_idx = st.selectbox(
                    "🥋 Turma *", 
                    options=range(len(turmas_opcoes)),
                    format_func=lambda x: turmas_opcoes[x],
                    index=0,
                    help="Selecione a turma do aluno"
                )
                turma = turmas_nomes[turma_selecionada_idx]
            else:
                turma = None
        
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
            
            if not turma or not turma.strip():
                st.error("❌ Turma é obrigatória!")
                return
            
            # Preparar dados
            dados_aluno = {
                'nome': nome.strip(),
                'status': status,
                'vencimentoDia': vencimento_dia,
                'ativoDesde': ativo_desde.strftime('%Y-%m-%d'),
                'turma': turma.strip()
            }
            
            # Adicionar contato se preenchido
            contato = {}
            if telefone and telefone.strip():
                contato['telefone'] = telefone.strip()
            if email and email.strip():
                contato['email'] = email.strip()
            
            if contato:
                dados_aluno['contato'] = contato
            
            # Adicionar dados opcionais
            if endereco and endereco.strip():
                dados_aluno['endereco'] = endereco.strip()
            
            # Cadastrar aluno
            try:
                aluno_id = alunos_service.criar_aluno(dados_aluno)
                st.session_state.aluno_cadastrado = {
                    'nome': nome,
                    'id': aluno_id
                }
                st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar aluno: {str(e)}")

def _mostrar_busca_alunos(alunos_service: AlunosService):
    """Mostra interface de busca de alunos"""
    
    st.markdown("### 🔍 Buscar Alunos")
    
    # Campo de busca
    termo_busca = st.text_input(
        "🔎 Digite o nome para buscar:",
        placeholder="Digite parte do nome do aluno...",
        help="A busca é realizada no nome do aluno"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)
    
    # Realizar busca
    if buscar and termo_busca and termo_busca.strip():
        try:
            resultados = alunos_service.buscar_por_nome(termo_busca.strip())
            
            if not resultados:
                st.warning(f"❓ Nenhum aluno encontrado com o termo: **{termo_busca}**")
                return
            
            st.success(f"✅ Encontrados **{len(resultados)}** aluno(s)")
            
            # Exibir resultados
            for i, aluno in enumerate(resultados):
                with st.expander(f"👤 {aluno.get('nome', 'N/A')} - {aluno.get('status', 'N/A').title()}", expanded=i==0):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📊 Status:** {aluno.get('status', 'N/A').title()}")
                        st.write(f"**📅 Vencimento:** Dia {aluno.get('vencimentoDia', 'N/A')}")
                        st.write(f"**📆 Ativo desde:** {aluno.get('ativoDesde', 'N/A')}")
                    
                    with col2:
                        contato = aluno.get('contato', {})
                        if isinstance(contato, dict):
                            st.write(f"**📱 Telefone:** {contato.get('telefone', 'N/A')}")
                            st.write(f"**📧 Email:** {contato.get('email', 'N/A')}")
                        st.write(f"**🥋 Turma:** {aluno.get('turma', 'N/A')}")
                    
                    # Ações rápidas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✏️ Editar", key=f"edit_{aluno.get('id')}"):
                            st.session_state.aluno_editando = aluno.get('id')
                            st.session_state.alunos_modo = 'editar'
                            st.rerun()
                    
                    with col2:
                        if aluno.get('status') == 'ativo':
                            if st.button(f"⏸️ Inativar", key=f"inativar_{aluno.get('id')}"):
                                if alunos_service.inativar_aluno(aluno.get('id')):
                                    st.success("Aluno inativado!")
                                    st.rerun()
                        else:
                            if st.button(f"▶️ Reativar", key=f"reativar_{aluno.get('id')}"):
                                if alunos_service.reativar_aluno(aluno.get('id')):
                                    st.success("Aluno reativado!")
                                    st.rerun()
                                    
        except Exception as e:
            st.error(f"❌ Erro na busca: {str(e)}")
    
    elif buscar and not termo_busca.strip():
        st.warning("⚠️ Digite um termo para buscar")

def _mostrar_estatisticas_alunos(alunos_service: AlunosService):
    """Mostra estatísticas dos alunos"""
    
    st.markdown("### 📊 Estatísticas dos Alunos")
    
    try:
        stats = alunos_service.obter_estatisticas()
        
        # Cards de estatísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Total de Alunos",
                value=stats['total'],
                help="Total de alunos cadastrados"
            )
        
        with col2:
            st.metric(
                label="✅ Alunos Ativos",
                value=stats['ativos'],
                delta=f"{(stats['ativos']/stats['total']*100):.1f}%" if stats['total'] > 0 else "0%",
                help="Alunos com status ativo"
            )
        
        with col3:
            st.metric(
                label="⏸️ Alunos Inativos",
                value=stats['inativos'],
                delta=f"{(stats['inativos']/stats['total']*100):.1f}%" if stats['total'] > 0 else "0%",
                help="Alunos com status inativo"
            )
        
        with col4:
            st.metric(
                label="🥋 Turmas",
                value=len(stats['por_turma']),
                help="Número de turmas diferentes"
            )
        
        # Gráfico de distribuição por turma
        if stats['por_turma']:
            st.markdown("---")
            st.markdown("#### 🥋 Distribuição por Turma")
            
            # Preparar dados para gráfico
            turma_df = pd.DataFrame(
                list(stats['por_turma'].items()),
                columns=['Turma', 'Quantidade']
            ).sort_values('Quantidade', ascending=False)
            
            # Gráfico de barras
            st.bar_chart(turma_df.set_index('Turma'))
            
            # Tabela detalhada
            st.markdown("##### 📋 Detalhes por Turma")
            st.dataframe(
                turma_df,
                column_config={
                    "Turma": "🥋 Turma",
                    "Quantidade": "👥 Quantidade"
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Análise de vencimentos
        st.markdown("---")
        st.markdown("#### 📅 Análise de Vencimentos")
        
        alunos = alunos_service.listar_alunos(status='ativo')
        if alunos:
            vencimentos = {}
            for aluno in alunos:
                dia = aluno.get('vencimentoDia', 0)
                vencimentos[dia] = vencimentos.get(dia, 0) + 1
            
            venc_df = pd.DataFrame(
                list(vencimentos.items()),
                columns=['Dia', 'Quantidade']
            ).sort_values('Dia')
            
            st.line_chart(venc_df.set_index('Dia'))
            
            st.info(f"💡 **Dicas:** Dia com mais vencimentos: **{max(vencimentos, key=vencimentos.get)}** ({max(vencimentos.values())} alunos)")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar estatísticas: {str(e)}")

def _mostrar_detalhes_aluno(alunos_service: AlunosService, aluno_id: str):
    """Mostra detalhes completos de um aluno"""
    
    try:
        aluno = alunos_service.buscar_aluno(aluno_id)
        
        if not aluno:
            st.error("❌ Aluno não encontrado!")
            return
        
        st.markdown(f"### 👤 Detalhes: **{aluno.get('nome', 'N/A')}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Dados Básicos")
            st.write(f"**ID:** {aluno.get('id', 'N/A')}")
            st.write(f"**Status:** {aluno.get('status', 'N/A').title()}")
            st.write(f"**Vencimento:** Dia {aluno.get('vencimentoDia', 'N/A')}")
            st.write(f"**Ativo desde:** {aluno.get('ativoDesde', 'N/A')}")
            if aluno.get('inativoDesde'):
                st.write(f"**Inativo desde:** {aluno.get('inativoDesde')}")
        
        with col2:
            st.markdown("#### 📞 Contato e Outros")
            contato = aluno.get('contato', {})
            if isinstance(contato, dict):
                st.write(f"**Telefone:** {contato.get('telefone', 'N/A')}")
                st.write(f"**Email:** {contato.get('email', 'N/A')}")
            st.write(f"**Endereço:** {aluno.get('endereco', 'N/A')}")
            st.write(f"**Turma:** {aluno.get('turma', 'N/A')}")
            if aluno.get('ultimoPagamentoYm'):
                st.write(f"**Último Pagamento:** {aluno.get('ultimoPagamentoYm')}")
        
        # Timestamps
        if aluno.get('createdAt') or aluno.get('updatedAt'):
            st.markdown("#### 🕒 Timestamps")
            if aluno.get('createdAt'):
                st.write(f"**Criado em:** {aluno.get('createdAt')}")
            if aluno.get('updatedAt'):
                st.write(f"**Atualizado em:** {aluno.get('updatedAt')}")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar detalhes: {str(e)}")

def _mostrar_formulario_editar_aluno(alunos_service: AlunosService):
    """Mostra formulário para editar aluno existente"""
    
    # Verificar se tem aluno para editar
    if 'aluno_editando' not in st.session_state or not st.session_state.aluno_editando:
        st.error("❌ Nenhum aluno selecionado para edição!")
        if st.button("📋 Voltar para Lista"):
            st.session_state.alunos_modo = 'lista'
            st.rerun()
        return
    
    aluno_id = st.session_state.aluno_editando
    
    try:
        # Carregar dados do aluno
        aluno = alunos_service.buscar_aluno(aluno_id)
        
        if not aluno:
            st.error("❌ Aluno não encontrado!")
            if st.button("📋 Voltar para Lista"):
                st.session_state.alunos_modo = 'lista'
                st.rerun()
            return
        
        st.markdown(f"### ✏️ Editar Aluno: **{aluno.get('nome', 'N/A')}**")
        
        # Botão voltar
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔙 Voltar para Lista", type="secondary"):
                st.session_state.alunos_modo = 'lista'
                del st.session_state.aluno_editando
                st.rerun()
        
        with st.form("form_editar_aluno", clear_on_submit=False):
            # Dados básicos
            st.markdown("#### 📝 Dados Básicos")
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input(
                    "👤 Nome Completo *", 
                    value=aluno.get('nome', ''),
                    placeholder="Digite o nome completo"
                )
                # Normalizar vencimento para valores válidos (10, 15, 25)
                venc_atual = int(aluno.get('vencimentoDia', 15))
                if venc_atual not in [10, 15, 25]:
                    # Converter valores inválidos para o mais próximo
                    if venc_atual < 13:
                        venc_atual = 10
                    elif venc_atual < 20:
                        venc_atual = 15
                    else:
                        venc_atual = 25
                
                vencimento_dia = st.selectbox(
                    "📅 Dia do Vencimento *", 
                    options=[10, 15, 25],
                    index=[10, 15, 25].index(venc_atual)
                )
            
            with col2:
                status = st.selectbox(
                    "📊 Status *", 
                    options=["ativo", "inativo"], 
                    index=0 if aluno.get('status') == 'ativo' else 1
                )
                # Manter a data original ou usar hoje se for reativação
                ativo_desde_value = aluno.get('ativoDesde', date.today().strftime('%Y-%m-%d'))
                if isinstance(ativo_desde_value, str):
                    try:
                        ativo_desde_date = datetime.strptime(ativo_desde_value, '%Y-%m-%d').date()
                    except:
                        ativo_desde_date = date.today()
                else:
                    ativo_desde_date = date.today()
                
                ativo_desde = st.date_input(
                    "📆 Ativo Desde *", 
                    value=ativo_desde_date,
                    min_value=date(2024, 1, 1),
                    max_value=date.today(),
                    help="Data de início na academia (entre 01/01/2024 e hoje)"
                )
            
            # Contato
            st.markdown("#### 📞 Contato")
            col1, col2 = st.columns(2)
            
            contato_atual = aluno.get('contato', {})
            if not isinstance(contato_atual, dict):
                contato_atual = {}
            
            with col1:
                telefone = st.text_input(
                    "📱 Telefone", 
                    value=contato_atual.get('telefone', ''),
                    placeholder="(11) 99999-9999"
                )
            
            with col2:
                email = st.text_input(
                    "📧 Email", 
                    value=contato_atual.get('email', ''),
                    placeholder="aluno@email.com"
                )
            
            # Outros dados
            st.markdown("#### 🏠 Dados Adicionais")
            col1, col2 = st.columns(2)
            
            with col1:
                endereco = st.text_input(
                    "🏠 Endereço", 
                    value=aluno.get('endereco', ''),
                    placeholder="Rua, número, bairro"
                )
            
            with col2:
                # Buscar turmas do banco de dados
                try:
                    if 'turmas_service' not in st.session_state:
                        st.session_state.turmas_service = TurmasService()
                    
                    turmas_service = st.session_state.turmas_service
                    turmas_db = turmas_service.listar_turmas(apenas_ativas=True)
                    
                    if turmas_db:
                        # Usar turmas do banco
                        turmas_opcoes = [f"{t['nome']} ({t['horarioInicio']} às {t['horarioFim']})" for t in turmas_db]
                        turmas_nomes = [t['nome'] for t in turmas_db]
                    else:
                        # Fallback se não houver turmas cadastradas
                        turmas_opcoes = ["⚠️ Nenhuma turma cadastrada"]
                        turmas_nomes = []
                        st.warning("⚠️ Nenhuma turma cadastrada. Por favor, cadastre turmas primeiro na página de Turmas.")
                    
                except Exception as e:
                    st.error(f"Erro ao carregar turmas: {str(e)}")
                    turmas_opcoes = ["⚠️ Erro ao carregar turmas"]
                    turmas_nomes = []
                
                # Definir índice da turma atual do aluno
                turma_atual = aluno.get('turma', '')
                if turmas_nomes and turma_atual in turmas_nomes:
                    turma_index = turmas_nomes.index(turma_atual)
                else:
                    turma_index = 0
                
                if turmas_nomes:
                    turma_selecionada_idx = st.selectbox(
                        "🥋 Turma *", 
                        options=range(len(turmas_opcoes)),
                        format_func=lambda x: turmas_opcoes[x],
                        index=turma_index,
                        help="Selecione a turma do aluno",
                        key="editar_turma_select"
                    )
                    turma = turmas_nomes[turma_selecionada_idx]
                else:
                    turma = turma_atual
            
            # Informações adicionais para status inativo
            if status == 'inativo':
                st.markdown("#### ⏸️ Dados de Inativação")
                inativo_desde_value = aluno.get('inativoDesde', date.today().strftime('%Y-%m-%d'))
                if isinstance(inativo_desde_value, str):
                    try:
                        inativo_desde_date = datetime.strptime(inativo_desde_value, '%Y-%m-%d').date()
                    except:
                        inativo_desde_date = date.today()
                else:
                    inativo_desde_date = date.today()
                
                inativo_desde = st.date_input("📅 Inativo Desde", value=inativo_desde_date)
            
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
                
                # Preparar dados de atualização
                dados_atualizacao = {
                    'nome': nome.strip(),
                    'status': status,
                    'vencimentoDia': vencimento_dia,
                    'ativoDesde': ativo_desde.strftime('%Y-%m-%d')
                }
                
                # Adicionar contato se preenchido
                contato = {}
                if telefone and telefone.strip():
                    contato['telefone'] = telefone.strip()
                if email and email.strip():
                    contato['email'] = email.strip()
                
                if contato:
                    dados_atualizacao['contato'] = contato
                
                # Adicionar dados opcionais
                if endereco and endereco.strip():
                    dados_atualizacao['endereco'] = endereco.strip()
                
                if turma and turma.strip():
                    dados_atualizacao['turma'] = turma.strip()
                
                # Adicionar data de inativação se necessário
                if status == 'inativo':
                    dados_atualizacao['inativoDesde'] = inativo_desde.strftime('%Y-%m-%d')
                else:
                    # Se mudou para ativo, remover data de inativação
                    dados_atualizacao['inativoDesde'] = None
                
                # Atualizar aluno
                try:
                    sucesso = alunos_service.atualizar_aluno(aluno_id, dados_atualizacao)
                    
                    if sucesso:
                        st.success(f"✅ Aluno **{nome}** atualizado com sucesso!")
                        
                        # Opções pós-edição
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📋 Voltar para Lista", type="secondary"):
                                st.session_state.alunos_modo = 'lista'
                                del st.session_state.aluno_editando
                                st.rerun()
                        
                        with col2:
                            if st.button("👁️ Ver Detalhes", type="secondary"):
                                _mostrar_detalhes_aluno(alunos_service, aluno_id)
                        
                        with col3:
                            if st.button("✏️ Continuar Editando", type="secondary"):
                                st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar aluno: {str(e)}")
        
        # Ações rápidas adicionais
        st.markdown("---")
        st.markdown("#### ⚡ Ações Rápidas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if aluno.get('status') == 'ativo':
                if st.button("⏸️ Inativar Aluno", use_container_width=True):
                    if alunos_service.inativar_aluno(aluno_id):
                        st.success("✅ Aluno inativado!")
                        st.rerun()
            else:
                if st.button("▶️ Reativar Aluno", use_container_width=True):
                    if alunos_service.reativar_aluno(aluno_id):
                        st.success("✅ Aluno reativado!")
                        st.rerun()
        
        with col2:
            if st.button("👁️ Ver Detalhes Completos", use_container_width=True):
                with st.expander("📄 Detalhes Completos", expanded=True):
                    _mostrar_detalhes_aluno(alunos_service, aluno_id)
        
        with col3:
            if st.button("🎓 Graduações", use_container_width=True):
                st.info("🚧 Graduações em desenvolvimento...")
        
        with col4:
            if st.button("💰 Pagamentos", use_container_width=True):
                st.info("🚧 Pagamentos em desenvolvimento...")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar aluno para edição: {str(e)}")
        if st.button("📋 Voltar para Lista"):
            st.session_state.alunos_modo = 'lista'
            if 'aluno_editando' in st.session_state:
                del st.session_state.aluno_editando
            st.rerun()