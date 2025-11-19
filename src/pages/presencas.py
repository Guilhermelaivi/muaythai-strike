"""
Gestão de Ausências por Turma
Marque apenas quem faltou - todos os outros são considerados presentes
"""
import streamlit as st
from datetime import date, datetime
from typing import List, Dict

from src.services.presencas_service import PresencasService
from src.services.alunos_service import AlunosService
from src.services.turmas_service import TurmasService


def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'ausencias_selecionadas' not in st.session_state:
        st.session_state.ausencias_selecionadas = set()
    if 'presencas_feedback_message' not in st.session_state:
        st.session_state.presencas_feedback_message = None
    if 'presencas_feedback_type' not in st.session_state:
        st.session_state.presencas_feedback_type = None


def exibir_gestao_ausencias():
    """Exibe interface de gestão de ausências por turma"""
    presencas_service = PresencasService()
    alunos_service = AlunosService()
    turmas_service = TurmasService()
    
    # Exibir feedback se houver
    if st.session_state.presencas_feedback_message:
        if st.session_state.presencas_feedback_type == "success":
            st.success(st.session_state.presencas_feedback_message)
        elif st.session_state.presencas_feedback_type == "warning":
            st.warning(st.session_state.presencas_feedback_message)
        elif st.session_state.presencas_feedback_type == "error":
            st.error(st.session_state.presencas_feedback_message)
        
        # Limpar feedback após exibir
        st.session_state.presencas_feedback_message = None
        st.session_state.presencas_feedback_type = None
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        # Carregar turmas
        turmas = turmas_service.listar_turmas(apenas_ativas=True)
        if not turmas:
            st.warning("⚠️ Nenhuma turma cadastrada no sistema.")
            return
        
        opcoes_turmas = [f"{t.get('nome', 'Sem nome')} ({t.get('horarioInicio', '')} - {t.get('horarioFim', '')})" for t in turmas]
        turma_map = {opcoes_turmas[i]: turmas[i] for i in range(len(turmas))}
        
        turma_selecionada = st.selectbox(
            "🏫 Selecione a Turma",
            options=opcoes_turmas,
            key="ausencias_turma"
        )
    
    with col2:
        data_selecionada = st.date_input(
            "📅 Data da Aula",
            value=date.today(),
            min_value=date(2024, 1, 1),  # Desde janeiro de 2024
            max_value=date.today(),  # Até hoje (não permite datas futuras)
            key="ausencias_data"
        )
    
    st.divider()
    
    # Filtrar alunos pela turma selecionada
    turma_obj = turma_map[turma_selecionada]
    turma_nome = turma_obj.get('nome', '')
    todos_alunos = alunos_service.listar_alunos()
    alunos = [a for a in todos_alunos if a.get('turma', '') == turma_nome]
    
    if not alunos:
        st.info("ℹ️ Nenhum aluno encontrado para esta turma.")
        return
    
    # Ordenar alunos por nome
    alunos_ordenados = sorted(alunos, key=lambda x: x.get('nome', ''))
    
    # Informações
    st.markdown(f"""
    ### 📋 Lista de Alunos - {turma_selecionada}
    **Total de alunos:** {len(alunos_ordenados)}  
    **Data:** {data_selecionada.strftime('%d/%m/%Y')}
    
    ✅ **Todos estão presentes por padrão**  
    ❌ **Marque apenas quem FALTOU**
    """)
    
    st.divider()
    
    # Verificar ausências já registradas
    ausencias_registradas = set()
    presencas_por_aluno = {}
    for aluno in alunos_ordenados:
        presenca = presencas_service.buscar_presenca_por_aluno_data(aluno.get('id'), data_selecionada)
        presencas_por_aluno[aluno.get('id')] = presenca
        # presente=False significa AUSENTE
        if presenca and presenca.get('presente') == False:
            ausencias_registradas.add(aluno.get('id'))
    
    # Inicializar ausências selecionadas com as já registradas
    if 'ausencias_inicializadas' not in st.session_state or st.session_state.get('ultima_data') != data_selecionada:
        st.session_state.ausencias_selecionadas = ausencias_registradas.copy()
        st.session_state.ausencias_inicializadas = True
        st.session_state.ultima_data = data_selecionada
    
    # Tabela de alunos
    st.markdown("#### 📋 Lista de Alunos - Marque as Ausências")
    
    # Cabeçalho da tabela
    header_cols = st.columns([0.5, 3, 2, 2, 1])
    with header_cols[0]:
        st.markdown("**#**")
    with header_cols[1]:
        st.markdown("**Nome**")
    with header_cols[2]:
        st.markdown("**Graduação**")
    with header_cols[3]:
        st.markdown("**Turma**")
    with header_cols[4]:
        st.markdown("**Ausente?**")
    
    st.divider()
    
    # Linhas da tabela
    for idx, aluno in enumerate(alunos_ordenados, 1):
        aluno_id = aluno.get('id')
        nome = aluno.get('nome', 'Sem nome')
        graduacao = aluno.get('graduacao', 'N/A')
        turma = aluno.get('turma', 'N/A')
        
        cols = st.columns([0.5, 3, 2, 2, 1])
        
        with cols[0]:
            st.markdown(f"**{idx}**")
        
        with cols[1]:
            # Exibir nome com ícone de status
            if aluno_id in st.session_state.ausencias_selecionadas:
                st.markdown(f"❌ {nome}")
            else:
                st.markdown(f"✅ {nome}")
        
        with cols[2]:
            st.markdown(graduacao)
        
        with cols[3]:
            st.markdown(turma)
        
        with cols[4]:
            is_ausente = st.checkbox(
                "Faltou",
                value=aluno_id in st.session_state.ausencias_selecionadas,
                key=f"ausencia_{aluno_id}",
                label_visibility="collapsed"
            )
            
            if is_ausente:
                st.session_state.ausencias_selecionadas.add(aluno_id)
            elif aluno_id in st.session_state.ausencias_selecionadas:
                st.session_state.ausencias_selecionadas.remove(aluno_id)
    
    st.divider()
    
    # Resumo
    total_ausentes = len(st.session_state.ausencias_selecionadas)
    total_presentes = len(alunos_ordenados) - total_ausentes
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Alunos", len(alunos_ordenados))
    with col2:
        st.metric("✅ Presentes", total_presentes)
    with col3:
        st.metric("❌ Ausentes", total_ausentes)
    
    # Botão de salvar
    if st.button("💾 Salvar Registros de Presença", type="primary", use_container_width=True):
        try:
            registros_salvos = 0
            for aluno in alunos_ordenados:
                aluno_id = aluno.get('id')
                # presente=False significa AUSENTE, presente=True significa PRESENTE
                presente = aluno_id not in st.session_state.ausencias_selecionadas
                
                presencas_service.registrar_presenca(
                    aluno_id=aluno_id,
                    data_presenca=data_selecionada,
                    presente=presente
                )
                registros_salvos += 1
            
            st.session_state.presencas_feedback_message = f"✅ {registros_salvos} registros salvos com sucesso! ({total_presentes} presentes, {total_ausentes} ausentes)"
            st.session_state.presencas_feedback_type = "success"
            st.session_state.ausencias_inicializadas = False  # Reset para próxima vez
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar registros: {str(e)}")


def show_presencas():
    """Função principal que exibe a página de ausências"""
    init_session_state()
    
    st.title("❌ Gestão de Ausências")
    st.caption("Marque apenas quem faltou - todos os demais serão marcados como presentes")
    
    exibir_gestao_ausencias()


def main():
    """Entry point da página"""
    show_presencas()


if __name__ == "__main__":
    main()
