import streamlit as st
from datetime import date
import pandas as pd
from src.services.graduacoes_service import GraduacoesService
from src.services.alunos_service import AlunosService
from src.services.turmas_service import TurmasService

def init_session_state():
    if 'graduacoes_feedback_message' not in st.session_state:
        st.session_state.graduacoes_feedback_message = None
    if 'graduacoes_feedback_type' not in st.session_state:
        st.session_state.graduacoes_feedback_type = None

def exibir_registrar_graduacao():
    graduacoes_service = GraduacoesService()
    alunos_service = AlunosService()
    turmas_service = TurmasService()
    
    if st.session_state.graduacoes_feedback_message:
        if st.session_state.graduacoes_feedback_type == "success":
            st.success(st.session_state.graduacoes_feedback_message)
        elif st.session_state.graduacoes_feedback_type == "warning":
            st.warning(st.session_state.graduacoes_feedback_message)
        elif st.session_state.graduacoes_feedback_type == "error":
            st.error(st.session_state.graduacoes_feedback_message)
        
        if st.button("OK, entendi", key="clear_feedback_grad"):
            st.session_state.graduacoes_feedback_message = None
            st.session_state.graduacoes_feedback_type = None
            st.rerun()
    
    try:
        # Filtro por turma
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            # Carregar turmas
            turmas = turmas_service.listar_turmas(apenas_ativas=True)
            if not turmas:
                st.warning("⚠️ Nenhuma turma cadastrada no sistema.")
                return
            
            opcoes_turmas = ["Todas as turmas"] + [f"{t.get('nome', 'Sem nome')} ({t.get('horarioInicio', '')} - {t.get('horarioFim', '')})" for t in turmas]
            turma_map = {opcoes_turmas[i+1]: turmas[i] for i in range(len(turmas))}
            
            turma_filtro = st.selectbox(
                "🏫 Filtrar por Turma",
                options=opcoes_turmas,
                key="grad_turma_filtro"
            )
        
        # Carregar e filtrar alunos
        todos_alunos = alunos_service.listar_alunos()
        if not todos_alunos:
            st.warning("Nenhum aluno cadastrado. Cadastre alunos primeiro.")
            return
        
        # Aplicar filtro de turma
        if turma_filtro == "Todas as turmas":
            alunos = todos_alunos
        else:
            turma_obj = turma_map[turma_filtro]
            turma_nome = turma_obj.get('nome', '')
            alunos = [a for a in todos_alunos if a.get('turma', '') == turma_nome]
        
        if not alunos:
            st.info("ℹ️ Nenhum aluno encontrado para esta turma.")
            return
        
        alunos.sort(key=lambda x: x.get('nome', ''))
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            opcoes_alunos = [f"{aluno['nome']} ({aluno.get('graduacao', 'Sem graduacao')})" 
                           for aluno in alunos]
            
            aluno_escolhido = st.selectbox(
                "Selecione o aluno:",
                options=opcoes_alunos,
                key="grad_aluno_select"
            )
            
            data_graduacao = st.date_input(
                "Data da graduacao:",
                value=date.today(),
                key="grad_data"
            )
        
        with col2:
            niveis_disponiveis = graduacoes_service.obter_niveis_graduacao_disponiveis()
            
            novo_nivel = st.selectbox(
                "Novo nivel:",
                options=niveis_disponiveis,
                key="grad_nivel"
            )
            
            observacoes = st.text_area(
                "Observacoes (opcional):",
                placeholder="Ex: Exame realizado com excelencia",
                key="grad_obs"
            )
        
        if st.button("Registrar Graduacao", type="primary", key="btn_registrar_grad"):
            if aluno_escolhido and novo_nivel:
                try:
                    indice_aluno = opcoes_alunos.index(aluno_escolhido)
                    aluno = alunos[indice_aluno]
                    
                    grad_id = graduacoes_service.registrar_graduacao(
                        aluno['id'], 
                        novo_nivel, 
                        data_graduacao,
                        observacoes if observacoes.strip() else None
                    )
                    
                    st.session_state.graduacoes_feedback_message = f"Graduacao registrada! {aluno['nome']} agora e {novo_nivel}"
                    st.session_state.graduacoes_feedback_type = "success"
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.graduacoes_feedback_message = f"Erro: {str(e)}"
                    st.session_state.graduacoes_feedback_type = "error"
                    st.rerun()
        
        # Exibir lista de alunos da turma
        st.divider()
        st.subheader(f"📋 Lista de Alunos ({len(alunos)} aluno{'s' if len(alunos) != 1 else ''})")
        
        # Preparar dados para a tabela
        dados_tabela = []
        for aluno in alunos:
            dados_tabela.append({
                "Nome": aluno.get('nome', 'N/A'),
                "Graduação Atual": aluno.get('graduacao', 'Sem graduação'),
                "Turma": aluno.get('turma', 'Sem turma'),
                "Responsável": aluno.get('responsavel', 'N/A'),
                "Contato": aluno.get('contato', 'N/A')
            })
        
        if dados_tabela:
            df = pd.DataFrame(dados_tabela)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum aluno para exibir.")
    
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")

def show_graduacoes():
    init_session_state()
    st.title("Registrar Graduacao")
    st.markdown("Registre promocoes e atualize graduacoes dos alunos")
    st.divider()
    exibir_registrar_graduacao()

def main():
    show_graduacoes()

if __name__ == "__main__":
    main()
