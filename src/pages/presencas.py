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
from src.utils.cache_service import CacheManager


def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'ausencias_selecionadas' not in st.session_state:
        st.session_state.ausencias_selecionadas = set()
    if 'presencas_feedback_message' not in st.session_state:
        st.session_state.presencas_feedback_message = None
    if 'presencas_feedback_type' not in st.session_state:
        st.session_state.presencas_feedback_type = None
    if 'presencas_gen' not in st.session_state:
        st.session_state.presencas_gen = 0


def exibir_gestao_ausencias():
    """Exibe interface de gestão de ausências por turma"""
    # Reusar instâncias via session_state (T25)
    if 'presencas_service' not in st.session_state:
        st.session_state.presencas_service = PresencasService()
    if 'alunos_service' not in st.session_state:
        st.session_state.alunos_service = AlunosService()
    if 'turmas_service' not in st.session_state:
        st.session_state.turmas_service = TurmasService()
    presencas_service = st.session_state.presencas_service
    alunos_service = st.session_state.alunos_service
    turmas_service = st.session_state.turmas_service
    cache_manager = CacheManager()
    
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
        modo = st.session_state.get('data_mode', 'operacional')
        min_data = date(2026, 1, 1) if modo == 'operacional' else date(2024, 1, 1)
        data_selecionada = st.date_input(
            "📅 Data da Aula",
            value=date.today(),
            min_value=min_data,
            max_value=date.today(),
            key="ausencias_data",
            format="DD/MM/YYYY"
        )
    
    st.divider()
    
    # Filtrar alunos pela turma selecionada
    turma_obj = turma_map[turma_selecionada]
    turma_nome = turma_obj.get('nome', '')
    todos_alunos = cache_manager.get_alunos_cached(alunos_service)
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
    
    # Verificar ausências já registradas (1 query em vez de N)
    try:
        presencas_do_dia = presencas_service.buscar_presencas_por_data(data_selecionada)
    except Exception as e:
        st.error(f"Erro ao carregar presenças: {e}")
        presencas_do_dia = {}
    ausencias_registradas = set()
    for aluno in alunos_ordenados:
        p = presencas_do_dia.get(aluno.get('id'))
        if p and p.get('presente') == False:
            ausencias_registradas.add(aluno.get('id'))
    
    # Reinicializar quando data ou turma mudam (incrementa gen para forçar novos checkboxes)
    contexto_atual = f"{data_selecionada}_{turma_nome}"
    if st.session_state.get('presencas_contexto') != contexto_atual:
        st.session_state.ausencias_selecionadas = ausencias_registradas.copy()
        st.session_state.presencas_contexto = contexto_atual
        st.session_state.presencas_gen += 1
    
    # Tabela de alunos
    st.markdown("#### 📋 Lista de Alunos - Marque as Ausências")
    
    # Cabeçalho da tabela
    header_cols = st.columns([0.5, 4, 1])
    with header_cols[0]:
        st.markdown("**#**")
    with header_cols[1]:
        st.markdown("**Nome**")
    with header_cols[2]:
        st.markdown("**Faltou?**")
    
    st.divider()
    
    # Linhas da tabela
    for idx, aluno in enumerate(alunos_ordenados, 1):
        aluno_id = aluno.get('id')
        nome = aluno.get('nome', 'Sem nome')
        
        cols = st.columns([0.5, 4, 1])
        
        with cols[0]:
            st.markdown(f"**{idx}**")
        
        with cols[2]:
            gen = st.session_state.presencas_gen
            is_ausente = st.checkbox(
                "Faltou",
                value=aluno_id in st.session_state.ausencias_selecionadas,
                key=f"ausencia_{aluno_id}_g{gen}",
                label_visibility="collapsed"
            )
            
            if is_ausente:
                st.session_state.ausencias_selecionadas.add(aluno_id)
            elif aluno_id in st.session_state.ausencias_selecionadas:
                st.session_state.ausencias_selecionadas.remove(aluno_id)
        
        with cols[1]:
            if aluno_id in st.session_state.ausencias_selecionadas:
                st.markdown(f"❌ {nome}")
            else:
                st.markdown(f"✅ {nome}")
    
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
            registros = []
            for aluno in alunos_ordenados:
                aluno_id = aluno.get('id')
                presente = aluno_id not in st.session_state.ausencias_selecionadas
                registros.append({'alunoId': aluno_id, 'presente': presente})
            
            registros_salvos = presencas_service.registrar_presencas_batch(registros, data_selecionada)
            
            st.session_state.presencas_feedback_message = f"✅ {len(registros)} registros processados ({total_presentes} presentes, {total_ausentes} ausentes)"
            st.session_state.presencas_feedback_type = "success"
            st.session_state.presencas_contexto = None  # Forçar reload do banco no próximo render
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar registros: {str(e)}")


def show_presencas():
    """Função principal que exibe a página de ausências"""
    init_session_state()
    
    st.title("✅ Gestão de Presenças")
    st.caption("ℹ️ Marque apenas quem faltou - todos os demais serão automaticamente marcados como presentes")
    
    exibir_gestao_ausencias()


def main():
    """Entry point da página"""
    show_presencas()


if __name__ == "__main__":
    main()
