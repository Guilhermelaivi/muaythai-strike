import streamlit as st
from datetime import date
import pandas as pd
from src.services.graduacoes_service import GraduacoesService
from src.services.alunos_service import AlunosService

def init_session_state():
    if 'graduacoes_feedback_message' not in st.session_state:
        st.session_state.graduacoes_feedback_message = None
    if 'graduacoes_feedback_type' not in st.session_state:
        st.session_state.graduacoes_feedback_type = None

def exibir_registrar_graduacao():
    graduacoes_service = GraduacoesService()
    alunos_service = AlunosService()
    
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
        alunos = alunos_service.listar_alunos()
        if not alunos:
            st.warning("Nenhum aluno cadastrado. Cadastre alunos primeiro.")
            return
        
        alunos.sort(key=lambda x: x.get('nome', ''))
        
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
