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
from src.services.pagamentos_service import PagamentosService
from src.services.presencas_service import PresencasService
from src.services.turmas_service import TurmasService
from src.utils.cache_service import get_cache_manager

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
    
    # Busca global: veio do sidebar com aluno específico
    if 'busca_aluno_id' in st.session_state:
        aluno_id = st.session_state.pop('busca_aluno_id')
        if st.button("← Voltar à lista", key="voltar_busca"):
            st.rerun()
        _mostrar_ficha_360(aluno_id)
        return
    
    # Modos de overlay (editar/completo) substituem as tabs
    if st.session_state.alunos_modo == 'editar':
        _mostrar_formulario_editar_aluno(alunos_service)
        return
    if st.session_state.alunos_modo == 'completo':
        _mostrar_formulario_novo_aluno(alunos_service)
        return
    
    # Navegação por tabs (sem rerun ao trocar de aba)
    tab_lista, tab_novo, tab_stats = st.tabs(
        ["📋 Lista de Alunos", "➕ Novo Aluno", "📊 Estatísticas"]
    )
    
    with tab_lista:
        _mostrar_lista_alunos(alunos_service)
    with tab_novo:
        _mostrar_quick_add_aluno(alunos_service)
    with tab_stats:
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
            help="Filtre por turma específica para melhor performance. 'Todas' carrega todos os alunos.",
            key="alunos_filtro_turma"
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
            index=filtro_status_idx,
            key="alunos_filtro_status"
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
            index=filtro_vencimento_idx,
            key="alunos_filtro_vencimento"
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
            }.get(x, x),
            key="alunos_filtro_ordenar"
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
            
            graduacao_atual = aluno.get('graduacao', 'Sem graduação')
            
            dados_tabela.append({
                'Nome': aluno.get('nome', ''),
                'Graduação': graduacao_atual,
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
            "Nome": st.column_config.TextColumn("👤 Nome", width="large"),
            "Graduação": st.column_config.TextColumn(
                "🥋 Graduação", 
                width="medium",
                help="Graduação atual do aluno. Selecione a linha para ver ficha completa."
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
            
            # Botões de ação
            col1, col2, col3 = st.columns(3)
            
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
                telefone = aluno_selecionado.get('Telefone', '')
                if telefone and telefone != 'N/A':
                    tel_limpo = ''.join(c for c in telefone if c.isdigit())
                    if tel_limpo:
                        st.markdown(f"[📱 WhatsApp](https://wa.me/55{tel_limpo})")
            
            # Ficha 360° do aluno
            _mostrar_ficha_360(aluno_selecionado['ID'])
        
        # Resumo
        st.markdown("---")
        st.markdown(f"**📊 Total: {len(alunos)} aluno(s) encontrado(s)**")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar alunos: {str(e)}")

def _mostrar_quick_add_aluno(alunos_service: AlunosService):
    """Formulário rápido de cadastro: Nome + Turma + Telefone"""
    
    st.markdown("### Cadastro Rápido")
    
    # Carregar turmas
    try:
        if 'turmas_service' not in st.session_state:
            st.session_state.turmas_service = TurmasService()
        turmas_db = st.session_state.turmas_service.listar_turmas(apenas_ativas=True)
        turmas_nomes = [t['nome'] for t in turmas_db] if turmas_db else []
        turmas_labels = [f"{t['nome']} ({t['horarioInicio']} - {t['horarioFim']})" for t in turmas_db] if turmas_db else []
    except Exception:
        turmas_nomes = []
        turmas_labels = []
    
    with st.form("form_quick_add", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome *", placeholder="Nome completo")
        with col2:
            if turmas_nomes:
                turma_idx = st.selectbox(
                    "Turma",
                    options=range(len(turmas_labels)),
                    format_func=lambda i: turmas_labels[i],
                )
                turma = turmas_nomes[turma_idx]
            else:
                turma = ""
                st.caption("Nenhuma turma cadastrada")
        with col3:
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
        
        submitted = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)
        
        if submitted:
            if not nome or not nome.strip():
                st.error("❌ Nome é obrigatório!")
            else:
                dados = {
                    'nome': nome.strip(),
                    'status': 'ativo',
                    'vencimentoDia': 15,
                    'ativoDesde': date.today().strftime('%Y-%m-%d'),
                    'turma': turma.strip() if turma else '',
                }
                if telefone and telefone.strip():
                    dados['contato'] = {'telefone': telefone.strip()}
                try:
                    aluno_id = alunos_service.criar_aluno(dados)
                    st.session_state.aluno_cadastrado = {'nome': nome.strip(), 'id': aluno_id}
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    # Sucesso
    if 'aluno_cadastrado' in st.session_state:
        info = st.session_state.aluno_cadastrado
        st.success(f"✅ **{info['nome']}** cadastrado!")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 Ver na Lista", type="primary", use_container_width=True):
                del st.session_state.aluno_cadastrado
                st.session_state.alunos_modo = 'lista'
                st.rerun()
        with c2:
            if st.button("➕ Cadastrar Outro", use_container_width=True):
                del st.session_state.aluno_cadastrado
                st.rerun()
    
    # Link para formulário completo
    with st.expander("📝 Precisa de mais campos? Use o formulário completo"):
        if st.button("Abrir Formulário Completo", use_container_width=True):
            st.session_state.alunos_modo = 'completo'
            st.rerun()


def _mostrar_formulario_novo_aluno(alunos_service: AlunosService):
    """Mostra formulário para cadastrar novo aluno"""
    
    if st.button("← Voltar ao Cadastro Rápido"):
        st.session_state.alunos_modo = 'lista'
        st.rerun()
    
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
    
    # Checkbox de responsável FORA do form para funcionar dinamicamente
    st.markdown("#### 👨‍👩‍👧‍👦 Responsável Legal")
    if 'possui_responsavel_novo' not in st.session_state:
        st.session_state.possui_responsavel_novo = False
    
    possui_responsavel = st.checkbox(
        "📋 Aluno é menor de idade e possui responsável legal",
        value=st.session_state.possui_responsavel_novo,
        help="Marque se o aluno tiver menos de 18 anos",
        key="check_responsavel_novo"
    )
    
    if possui_responsavel != st.session_state.possui_responsavel_novo:
        st.session_state.possui_responsavel_novo = possui_responsavel
        st.rerun()
    
    st.markdown("---")
    
    with st.form("form_novo_aluno", clear_on_submit=True):
        # Dados básicos
        st.markdown("#### Dados Básicos")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo", placeholder="Digite o nome completo")
            vencimento_dia = st.selectbox(
                "Dia do Vencimento", 
                options=[10, 15, 25],
                index=1
            )
        
        with col2:
            status = st.selectbox("Status", options=["ativo", "inativo"], index=0)
            ativo_desde = st.date_input(
                "Ativo Desde", 
                value=date.today(),
                min_value=date(2024, 1, 1),
                max_value=date.today(),
                help="Data de início na academia",
                format="DD/MM/YYYY"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            data_nascimento_aluno = st.date_input(
                "Data de Nascimento",
                value=None,
                min_value=date(1920, 1, 1),
                max_value=date.today(),
                key="data_nasc_aluno_novo",
                format="DD/MM/YYYY"
            )
        with col2:
            st.write("")
        
        # Contato
        st.markdown("#### Contato")
        col1, col2 = st.columns(2)
        
        with col1:
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
        
        with col2:
            email = st.text_input("Email", placeholder="aluno@email.com")
        
        # Campos do responsável aparecem SE o checkbox estiver marcado
        if st.session_state.possui_responsavel_novo:
            st.markdown("#### Responsável Legal")
            col1, col2 = st.columns(2)
            
            with col1:
                responsavel_nome = st.text_input(
                    "Nome do Responsável",
                    placeholder="Nome completo",
                    key="resp_nome_novo"
                )
                responsavel_cpf = st.text_input(
                    "CPF do Responsável",
                    placeholder="000.000.000-00",
                    key="resp_cpf_novo"
                )
            
            with col2:
                responsavel_rg = st.text_input(
                    "RG do Responsável",
                    placeholder="00.000.000-0",
                    key="resp_rg_novo"
                )
                responsavel_telefone = st.text_input(
                    "Telefone do Responsável",
                    placeholder="(11) 99999-9999",
                    key="resp_tel_novo"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                responsavel_data_nascimento = st.date_input(
                    "Nascimento do Responsável",
                    value=None,
                    min_value=date(1920, 1, 1),
                    max_value=date.today(),
                    key="resp_data_nasc_novo",
                    format="DD/MM/YYYY"
                )
            with col2:
                st.write("")
        else:
            responsavel_nome = None
            responsavel_cpf = None
            responsavel_rg = None
            responsavel_telefone = None
            responsavel_data_nascimento = None
        
        # Outros dados
        st.markdown("#### Dados Adicionais")
        col1, col2 = st.columns(2)
        
        with col1:
            endereco = st.text_input("Endereço", placeholder="Rua, número, bairro")
        
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
            
            turma = ""
            if turmas_nomes:
                turmas_opcoes_exibicao = ["(Não informar agora)"] + turmas_opcoes
                turmas_nomes_valores = [""] + turmas_nomes
                turma_selecionada_idx = st.selectbox(
                    "Turma",
                    options=range(len(turmas_opcoes_exibicao)),
                    format_func=lambda x: turmas_opcoes_exibicao[x],
                    index=0,
                    help="Opcional — pode preencher depois."
                )
                turma = turmas_nomes_valores[turma_selecionada_idx]
        
        # Observações
        observacoes = st.text_area("Observações", placeholder="Informações adicionais sobre o aluno...", height=80)
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)
        
        # Processar formulário
        if submitted:
            # Preparar dados
            dados_aluno = {
                'nome': nome.strip() if nome else "",
                'status': status,
                'vencimentoDia': vencimento_dia,
                'ativoDesde': ativo_desde.strftime('%Y-%m-%d') if ativo_desde else "",
                'turma': turma.strip() if turma else ""
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
            
            # Adicionar observações
            if observacoes and observacoes.strip():
                dados_aluno['observacoes'] = observacoes.strip()
            
            # Adicionar data de nascimento do aluno
            if data_nascimento_aluno:
                dados_aluno['dataNascimento'] = data_nascimento_aluno.strftime('%Y-%m-%d')
            
            # Adicionar dados do responsável apenas se algum campo foi preenchido
            if st.session_state.possui_responsavel_novo:
                responsavel_data = {}
                if responsavel_nome and responsavel_nome.strip():
                    responsavel_data['nome'] = responsavel_nome.strip()
                if responsavel_telefone and responsavel_telefone.strip():
                    responsavel_data['telefone'] = responsavel_telefone.strip()
                if responsavel_cpf and responsavel_cpf.strip():
                    responsavel_data['cpf'] = responsavel_cpf.strip()
                if responsavel_rg and responsavel_rg.strip():
                    responsavel_data['rg'] = responsavel_rg.strip()
                if responsavel_data_nascimento:
                    responsavel_data['dataNascimento'] = responsavel_data_nascimento.strftime('%Y-%m-%d')
                if responsavel_data:
                    dados_aluno['responsavel'] = responsavel_data
            
            # Cadastrar aluno
            try:
                aluno_id = alunos_service.criar_aluno(dados_aluno)
                st.session_state.aluno_cadastrado = {
                    'nome': (nome.strip() if nome and nome.strip() else "(Sem nome)"),
                    'id': aluno_id
                }
                # Limpar checkbox ao cadastrar
                st.session_state.possui_responsavel_novo = False
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
            
            # Preparar dados para tabela
            turma_df = pd.DataFrame(
                list(stats['por_turma'].items()),
                columns=['Turma', 'Quantidade']
            ).sort_values('Quantidade', ascending=False)
            
            # Barras visuais com progress bars
            for _, row in turma_df.iterrows():
                max_qtd = turma_df['Quantidade'].max()
                col_nome, col_barra, col_num = st.columns([2, 6, 1])
                with col_nome:
                    st.markdown(f"**{row['Turma']}**")
                with col_barra:
                    st.progress(row['Quantidade'] / max_qtd if max_qtd > 0 else 0)
                with col_num:
                    st.markdown(f"**{row['Quantidade']}**")
        
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
            
            # Barras visuais para vencimentos
            for _, row in venc_df.iterrows():
                max_qtd = venc_df['Quantidade'].max()
                col_dia, col_barra, col_num = st.columns([2, 6, 1])
                with col_dia:
                    st.markdown(f"Dia **{int(row['Dia'])}**")
                with col_barra:
                    st.progress(row['Quantidade'] / max_qtd if max_qtd > 0 else 0)
                with col_num:
                    st.markdown(f"**{row['Quantidade']}**")
            
            st.info(f"💡 Dia com mais vencimentos: **{max(vencimentos, key=vencimentos.get)}** ({max(vencimentos.values())} alunos)")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar estatísticas: {str(e)}")

def _mostrar_ficha_360(aluno_id: str):
    """Mostra ficha 360° do aluno: dados, pagamentos, presenças e graduações"""
    try:
        alunos_service = st.session_state.get('alunos_service') or AlunosService()
        aluno = alunos_service.buscar_aluno(aluno_id)
        if not aluno:
            st.error("❌ Aluno não encontrado!")
            return

        # Se veio da tela de cobranças, mostrar formulário de pagamento em destaque
        veio_de_cobranca = st.session_state.pop('ficha_tab_default', None) == 'pagamentos'
        if veio_de_cobranca:
            st.markdown("### 💰 Registrar Pagamento")
            st.info(f"Aluno: **{aluno.get('nome', '')}** | Turma: {aluno.get('turma', 'N/A')} | Venc: dia {aluno.get('vencimentoDia', 'N/A')}")
            pag_service = PagamentosService()
            cache_manager = get_cache_manager()
            hoje = date.today()
            _nomes_meses = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            modo = st.session_state.get('data_mode', 'operacional')
            min_ano = 2026 if modo == 'operacional' else 2020
            opcoes_ym = []
            for a in range(min_ano, hoje.year + 1):
                for m in range(1, 13):
                    if a == hoje.year and m > hoje.month:
                        break
                    opcoes_ym.append((a, m, f"{a}-{m:02d} ({_nomes_meses[m]})"))

            col_ym, col_val = st.columns(2)
            with col_ym:
                default_idx = next(
                    (i for i, (a, m, _) in enumerate(opcoes_ym) if a == max(hoje.year, min_ano) and m == hoje.month),
                    0
                )
                ym_sel = st.selectbox(
                    "Mês/Ano de Referência",
                    options=opcoes_ym,
                    index=default_idx,
                    format_func=lambda x: x[2],
                    key=f"cobranca_pag_ym_{aluno_id}"
                )
            with col_val:
                valor_pag = st.number_input(
                    "Valor (R$)",
                    min_value=0.01, step=0.01, format="%.2f", value=150.0,
                    key=f"cobranca_pag_val_{aluno_id}"
                )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Confirmar Pagamento", key=f"cobranca_pag_btn_{aluno_id}", type="primary", use_container_width=True):
                    ano_ref, mes_ref = ym_sel[0], ym_sel[1]
                    existente = pag_service.buscar_pagamento_por_aluno_mes(aluno_id, ano_ref, mes_ref)
                    if existente:
                        st.warning(f"⚠️ Já existe pagamento para {mes_ref:02d}/{ano_ref}")
                    else:
                        dados = {
                            'alunoId': aluno_id,
                            'alunoNome': aluno.get('nome', ''),
                            'ano': ano_ref,
                            'mes': mes_ref,
                            'valor': valor_pag,
                            'status': 'pago',
                            'exigivel': True
                        }
                        pag_service.criar_pagamento(dados)
                        cache_manager.invalidate_pagamento_cache(f"{ano_ref:04d}-{mes_ref:02d}")
                        st.toast(f"✅ Pagamento de {aluno.get('nome', '')} registrado! R$ {valor_pag:.2f} — {mes_ref:02d}/{ano_ref}")
                        # Voltar para pagamentos
                        st.session_state.current_page = "💰 Pagamentos"
                        st.rerun()
            with col_btn2:
                if st.button("← Cancelar", key="cobranca_cancelar", use_container_width=True):
                    st.session_state.current_page = "💰 Pagamentos"
                    st.rerun()

            st.divider()

        tab_dados, tab_pag, tab_grad = st.tabs(
            ["📝 Dados", "💰 Pagamentos", "🥋 Graduações"]
        )

        # --- Aba Dados ---
        with tab_dados:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {aluno.get('status', 'N/A').title()}")
                st.write(f"**Vencimento:** Dia {aluno.get('vencimentoDia', 'N/A')}")
                st.write(f"**Turma:** {aluno.get('turma', 'N/A')}")
                st.write(f"**Ativo desde:** {aluno.get('ativoDesde', 'N/A')}")
                if aluno.get('dataNascimento'):
                    st.write(f"**Nascimento:** {aluno.get('dataNascimento')}")
            with col2:
                contato = aluno.get('contato', {})
                if isinstance(contato, dict):
                    st.write(f"**Telefone:** {contato.get('telefone', 'N/A')}")
                    st.write(f"**Email:** {contato.get('email', 'N/A')}")
                st.write(f"**Endereço:** {aluno.get('endereco', 'N/A')}")

            responsavel = aluno.get('responsavel', {})
            if responsavel and isinstance(responsavel, dict):
                st.markdown("##### 👨‍👩‍👧‍👦 Responsável")
                st.write(f"{responsavel.get('nome', 'N/A')} — Tel: {responsavel.get('telefone', 'N/A')}")

            obs = aluno.get('observacoes', '')
            if obs and obs.strip():
                st.info(obs)

        # --- Aba Pagamentos ---
        with tab_pag:
            try:
                pag_service = PagamentosService()
                cache_manager = get_cache_manager()
                pagamentos = pag_service.listar_pagamentos_por_aluno(aluno_id)

                # Resumo rápido
                total_pago = sum(1 for p in pagamentos if p.get('status') == 'pago')
                total_pendente = sum(1 for p in pagamentos if p.get('status') in ('devedor', 'inadimplente'))
                valor_total = sum(p.get('valor', 0) for p in pagamentos if p.get('status') == 'pago')
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Pagos", total_pago)
                with m2:
                    st.metric("Pendentes", total_pendente)
                with m3:
                    st.metric("Total recebido", f"R$ {valor_total:,.2f}")

                # Registrar novo pagamento
                with st.expander("➕ Registrar Pagamento", expanded=False):
                    hoje = date.today()
                    _nomes_meses = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    modo = st.session_state.get('data_mode', 'operacional')
                    min_ano = 2026 if modo == 'operacional' else 2020
                    opcoes_ym = []
                    for a in range(min_ano, hoje.year + 1):
                        for m in range(1, 13):
                            if a == hoje.year and m > hoje.month:
                                break
                            opcoes_ym.append((a, m, f"{a}-{m:02d} ({_nomes_meses[m]})"))

                    col_ym, col_val = st.columns(2)
                    with col_ym:
                        default_idx = next(
                            (i for i, (a, m, _) in enumerate(opcoes_ym) if a == max(hoje.year, min_ano) and m == hoje.month),
                            0
                        )
                        ym_sel = st.selectbox(
                            "Mês/Ano",
                            options=opcoes_ym,
                            index=default_idx,
                            format_func=lambda x: x[2],
                            key=f"ficha_pag_ym_{aluno_id}"
                        )
                    with col_val:
                        valor_pag = st.number_input(
                            "Valor (R$)",
                            min_value=0.01, step=0.01, format="%.2f", value=150.0,
                            key=f"ficha_pag_val_{aluno_id}"
                        )

                    if st.button("✅ Registrar Pagamento", key=f"ficha_pag_btn_{aluno_id}", type="primary", use_container_width=True):
                        ano_ref, mes_ref = ym_sel[0], ym_sel[1]
                        # Verificar se já existe
                        existente = pag_service.buscar_pagamento_por_aluno_mes(aluno_id, ano_ref, mes_ref)
                        if existente:
                            st.warning(f"⚠️ Já existe pagamento para {mes_ref:02d}/{ano_ref}")
                        else:
                            dados = {
                                'alunoId': aluno_id,
                                'alunoNome': aluno.get('nome', ''),
                                'ano': ano_ref,
                                'mes': mes_ref,
                                'valor': valor_pag,
                                'status': 'pago',
                                'exigivel': True
                            }
                            pag_service.criar_pagamento(dados)
                            cache_manager.invalidate_pagamento_cache(f"{ano_ref:04d}-{mes_ref:02d}")
                            st.toast(f"✅ Pagamento {mes_ref:02d}/{ano_ref} registrado!")
                            st.rerun()

                st.divider()

                # Ações rápidas para pendentes
                if total_pendente > 0:
                    st.markdown("##### Pendentes")
                    for p in pagamentos:
                        if p.get('status') in ('devedor', 'inadimplente'):
                            c1, c2 = st.columns([4, 2])
                            with c1:
                                emoji = '🔴' if p.get('status') == 'inadimplente' else '🔔'
                                label = 'Inadimplente' if p.get('status') == 'inadimplente' else 'A Cobrar'
                                st.markdown(f"{emoji} **{p.get('ym', '')}** — R$ {p.get('valor', 0):.2f} ({label})")
                            with c2:
                                if st.button("💰 Marcar Pago", key=f"ficha_pag_{p.get('id')}", use_container_width=True):
                                    pag_service.marcar_como_pago(p.get('id'))
                                    cache_manager.invalidate_pagamento_cache(p.get('ym'))
                                    st.toast(f"✅ Pagamento {p.get('ym')} marcado como pago!")
                                    st.rerun()
                    st.divider()

                # Histórico completo
                if pagamentos:
                    st.markdown("##### Histórico")
                    STATUS_MAP = {
                        'pago': '🟢 Pago', 'devedor': '🔔 A Cobrar',
                        'inadimplente': '🔴 Inadimplente', 'ausente': '⚪ Ausente'
                    }
                    df_pag = pd.DataFrame([{
                        'Mês': p.get('ym', ''),
                        'Valor': p.get('valor', 0),
                        'Status': STATUS_MAP.get(p.get('status', ''), p.get('status', '')),
                    } for p in pagamentos])
                    st.dataframe(
                        df_pag, hide_index=True, use_container_width=True,
                        column_config={'Valor': st.column_config.NumberColumn(format="R$ %.2f")},
                    )
                else:
                    st.info("Nenhum pagamento registrado.")
            except Exception as e:
                st.error(f"Erro ao carregar pagamentos: {e}")

        # --- Aba Graduações ---
        with tab_grad:
            try:
                grad_service = st.session_state.get('graduacoes_service') or GraduacoesService()
                historico = grad_service.listar_graduacoes_aluno(aluno_id)

                st.write(f"**Graduação atual:** {aluno.get('graduacao', 'Sem Graduação')}")

                # Formulário para registrar nova graduação
                with st.expander("🥋 Registrar Nova Graduação", expanded=not bool(historico)):
                    niveis = grad_service.obter_niveis_graduacao_disponiveis()
                    col_n, col_d = st.columns(2)
                    with col_n:
                        novo_nivel = st.selectbox(
                            "Novo nível",
                            options=niveis,
                            key=f"ficha_grad_nivel_{aluno_id}"
                        )
                    with col_d:
                        data_grad = st.date_input(
                            "Data da graduação",
                            value=date.today(),
                            key=f"ficha_grad_data_{aluno_id}",
                            format="DD/MM/YYYY"
                        )
                    obs_grad = st.text_input(
                        "Observações (opcional)",
                        key=f"ficha_grad_obs_{aluno_id}",
                        placeholder="Ex: Exame realizado com excelência"
                    )
                    if st.button("✅ Registrar Graduação", key=f"ficha_grad_btn_{aluno_id}", type="primary", use_container_width=True):
                        try:
                            grad_service.registrar_graduacao(
                                aluno_id,
                                novo_nivel,
                                data_grad,
                                obs_grad.strip() if obs_grad and obs_grad.strip() else None
                            )
                            st.toast(f"✅ Graduação registrada: {novo_nivel}")
                            st.rerun()
                        except Exception as eg:
                            st.error(f"Erro ao registrar graduação: {eg}")

                st.divider()

                # Histórico
                if not historico:
                    st.info("Nenhuma graduação registrada.")
                else:
                    st.markdown("##### Histórico")
                    for idx, grad in enumerate(reversed(historico), 1):
                        obs_g = f" — _{grad.get('obs')}_" if grad.get('obs') else ""
                        st.markdown(f"{idx}. **{grad.get('nivel', 'N/A')}** — {grad.get('data', 'N/A')}{obs_g}")
            except Exception as e:
                st.error(f"Erro ao carregar graduações: {e}")

    except Exception as e:
        st.error(f"❌ Erro ao carregar ficha: {str(e)}")

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
        
        # Feedback visual de atualização
        if st.session_state.pop('aluno_atualizado', False):
            st.success(f"✅ Aluno **{aluno.get('nome', '')}** atualizado com sucesso!")
        
        # Botão voltar
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔙 Voltar para Lista", type="secondary"):
                st.session_state.alunos_modo = 'lista'
                del st.session_state.aluno_editando
                # Limpar estado do checkbox
                chave_estado = f'possui_responsavel_edit_{aluno_id}'
                if chave_estado in st.session_state:
                    del st.session_state[chave_estado]
                st.rerun()
        
        # Checkbox de responsável FORA do form para funcionar dinamicamente
        st.markdown("#### 👨‍👩‍👧‍👦 Responsável Legal")
        responsavel_atual = aluno.get('responsavel', {})
        
        # Inicializar estado baseado no aluno atual
        # Usa o ID do aluno como chave para evitar conflito entre diferentes alunos
        chave_estado = f'possui_responsavel_edit_{aluno_id}'
        if chave_estado not in st.session_state:
            st.session_state[chave_estado] = bool(responsavel_atual and isinstance(responsavel_atual, dict))
        
        possui_responsavel = st.checkbox(
            "📋 Aluno é menor de idade e possui responsável legal",
            value=st.session_state[chave_estado],
            help="Marque se o aluno tiver menos de 18 anos",
            key=f"check_responsavel_edit_{aluno_id}"
        )
        
        if possui_responsavel != st.session_state[chave_estado]:
            st.session_state[chave_estado] = possui_responsavel
            st.rerun()
        
        st.markdown("---")
        
        with st.form("form_editar_aluno", clear_on_submit=False):
            # Dados básicos
            st.markdown("#### Dados Básicos")
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input(
                    "Nome Completo", 
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
                    "Dia do Vencimento", 
                    options=[10, 15, 25],
                    index=[10, 15, 25].index(venc_atual)
                )
            
            with col2:
                status = st.selectbox(
                    "Status", 
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
                    "Ativo Desde", 
                    value=ativo_desde_date,
                    min_value=date(2024, 1, 1),
                    max_value=date.today(),
                    help="Data de início na academia",
                    format="DD/MM/YYYY"
                )
            
            # Data de nascimento do aluno
            col1, col2 = st.columns(2)
            with col1:
                # Carregar data de nascimento existente
                data_nasc_aluno_atual = aluno.get('dataNascimento', '')
                if data_nasc_aluno_atual:
                    try:
                        data_nasc_aluno_date = datetime.strptime(data_nasc_aluno_atual, '%Y-%m-%d').date()
                    except:
                        data_nasc_aluno_date = None
                else:
                    data_nasc_aluno_date = None
                
                data_nascimento_aluno = st.date_input(
                    "Data de Nascimento",
                    value=data_nasc_aluno_date,
                    min_value=date(1920, 1, 1),
                    max_value=date.today(),
                    key="data_nasc_aluno_edit",
                    format="DD/MM/YYYY"
                )
            with col2:
                st.write("")  # Spacer
            
            # Contato
            st.markdown("#### Contato")
            col1, col2 = st.columns(2)
            
            contato_atual = aluno.get('contato', {})
            if not isinstance(contato_atual, dict):
                contato_atual = {}
            
            with col1:
                telefone = st.text_input(
                    "Telefone", 
                    value=contato_atual.get('telefone', ''),
                    placeholder="(11) 99999-9999"
                )
            
            with col2:
                email = st.text_input(
                    "Email", 
                    value=contato_atual.get('email', ''),
                    placeholder="aluno@email.com"
                )
            
            # Campos do responsável aparecem SE o checkbox estiver marcado
            chave_estado = f'possui_responsavel_edit_{aluno_id}'
            if st.session_state.get(chave_estado, False):
                st.markdown("#### Responsável Legal")
                responsavel_atual = aluno.get('responsavel', {})
                if not isinstance(responsavel_atual, dict):
                    responsavel_atual = {}
                
                col1, col2 = st.columns(2)
                
                with col1:
                    responsavel_nome = st.text_input(
                        "Nome do Responsável",
                        value=responsavel_atual.get('nome', ''),
                        placeholder="Nome completo",
                        key="resp_nome_edit"
                    )
                    responsavel_cpf = st.text_input(
                        "CPF do Responsável",
                        value=responsavel_atual.get('cpf', ''),
                        placeholder="000.000.000-00",
                        key="resp_cpf_edit"
                    )
                
                with col2:
                    responsavel_rg = st.text_input(
                        "RG do Responsável",
                        value=responsavel_atual.get('rg', ''),
                        placeholder="00.000.000-0",
                        key="resp_rg_edit"
                    )
                    responsavel_telefone = st.text_input(
                        "Telefone do Responsável",
                        value=responsavel_atual.get('telefone', ''),
                        placeholder="(11) 99999-9999",
                        key="resp_tel_edit"
                    )
                
                # Data de nascimento do responsável
                col1, col2 = st.columns(2)
                with col1:
                    # Carregar data de nascimento do responsável existente
                    data_nasc_resp_atual = responsavel_atual.get('dataNascimento', '')
                    if data_nasc_resp_atual:
                        try:
                            data_nasc_resp_date = datetime.strptime(data_nasc_resp_atual, '%Y-%m-%d').date()
                        except:
                            data_nasc_resp_date = None
                    else:
                        data_nasc_resp_date = None
                    
                    responsavel_data_nascimento = st.date_input(
                        "Nascimento do Responsável",
                        value=data_nasc_resp_date,
                        min_value=date(1920, 1, 1),
                        max_value=date.today(),
                        key="resp_data_nasc_edit",
                        format="DD/MM/YYYY"
                    )
                with col2:
                    st.write("")  # Spacer
            else:
                responsavel_nome = None
                responsavel_cpf = None
                responsavel_rg = None
                responsavel_telefone = None
                responsavel_data_nascimento = None
            
            # Outros dados
            st.markdown("#### Dados Adicionais")
            col1, col2 = st.columns(2)
            
            with col1:
                endereco = st.text_input(
                    "Endereço", 
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
                        "Turma *", 
                        options=range(len(turmas_opcoes)),
                        format_func=lambda x: turmas_opcoes[x],
                        index=turma_index,
                        help="Selecione a turma do aluno",
                        key="editar_turma_select"
                    )
                    turma = turmas_nomes[turma_selecionada_idx]
                else:
                    turma = turma_atual
            
            # Observações
            observacoes = st.text_area("Observações", value=aluno.get('observacoes', ''), placeholder="Informações adicionais...", height=80, key="editar_observacoes")
            
            # Informações adicionais para status inativo
            if status == 'inativo':
                st.markdown("#### Dados de Inativação")
                inativo_desde_value = aluno.get('inativoDesde', date.today().strftime('%Y-%m-%d'))
                if isinstance(inativo_desde_value, str):
                    try:
                        inativo_desde_date = datetime.strptime(inativo_desde_value, '%Y-%m-%d').date()
                    except:
                        inativo_desde_date = date.today()
                else:
                    inativo_desde_date = date.today()
                
                inativo_desde = st.date_input("Inativo Desde", value=inativo_desde_date, format="DD/MM/YYYY")
            
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
                # Dados do responsável são opcionais
                chave_estado = f'possui_responsavel_edit_{aluno_id}'
                
                # Preparar dados de atualização
                dados_atualizacao = {
                    'nome': nome.strip() if nome else "",
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
                
                # Adicionar observações
                if observacoes and observacoes.strip():
                    dados_atualizacao['observacoes'] = observacoes.strip()
                else:
                    dados_atualizacao['observacoes'] = None
                
                # Adicionar data de nascimento do aluno
                if data_nascimento_aluno:
                    dados_atualizacao['dataNascimento'] = data_nascimento_aluno.strftime('%Y-%m-%d')
                else:
                    dados_atualizacao['dataNascimento'] = None
                
                # Adicionar ou remover dados do responsável
                chave_estado = f'possui_responsavel_edit_{aluno_id}'
                if st.session_state.get(chave_estado, False):
                    responsavel_data = {}
                    if responsavel_nome and responsavel_nome.strip():
                        responsavel_data['nome'] = responsavel_nome.strip()
                    if responsavel_telefone and responsavel_telefone.strip():
                        responsavel_data['telefone'] = responsavel_telefone.strip()
                    if responsavel_cpf and responsavel_cpf.strip():
                        responsavel_data['cpf'] = responsavel_cpf.strip()
                    if responsavel_rg and responsavel_rg.strip():
                        responsavel_data['rg'] = responsavel_rg.strip()
                    if responsavel_data_nascimento:
                        responsavel_data['dataNascimento'] = responsavel_data_nascimento.strftime('%Y-%m-%d')
                    dados_atualizacao['responsavel'] = responsavel_data if responsavel_data else None
                else:
                    # Se desmarcou, remover dados do responsável
                    dados_atualizacao['responsavel'] = None
                
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
                        # Limpar cache para forçar recarregamento
                        st.cache_data.clear()
                        # Limpar estado do checkbox
                        chave_estado = f'possui_responsavel_edit_{aluno_id}'
                        if chave_estado in st.session_state:
                            del st.session_state[chave_estado]
                        st.session_state.aluno_atualizado = True
                        st.toast(f"✅ Aluno {nome} atualizado com sucesso!")
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
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar aluno para edição: {str(e)}")
        if st.button("📋 Voltar para Lista"):
            st.session_state.alunos_modo = 'lista'
            if 'aluno_editando' in st.session_state:
                del st.session_state.aluno_editando
            st.rerun()