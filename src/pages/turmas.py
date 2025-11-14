import streamlit as st
import pandas as pd
from src.services.turmas_service import TurmasService

def show_turmas():
    if 'turmas_service' not in st.session_state:
        st.session_state.turmas_service = TurmasService()
    
    turmas_service = st.session_state.turmas_service
    st.markdown("## Gerenciamento de Turmas")
    
    if 'turmas_modo' not in st.session_state:
        st.session_state.turmas_modo = 'lista'
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Lista de Turmas", use_container_width=True):
            st.session_state.turmas_modo = 'lista'
            st.rerun()
    
    with col2:
        if st.button("Nova Turma", use_container_width=True):
            st.session_state.turmas_modo = 'nova'
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.turmas_modo == 'lista':
        mostrar_lista(turmas_service)
    elif st.session_state.turmas_modo == 'nova':
        mostrar_formulario(turmas_service)

def mostrar_lista(turmas_service):
    st.markdown("### Lista de Turmas")
    
    turmas = turmas_service.listar_turmas()
    
    if not turmas:
        st.info("Nenhuma turma cadastrada.")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Turmas", len(turmas))
    with col2:
        ativos = sum(1 for t in turmas if t.get('ativo', True))
        st.metric("Turmas Ativas", ativos)
    with col3:
        inativos = sum(1 for t in turmas if not t.get('ativo', True))
        st.metric("Turmas Inativas", inativos)
    
    st.markdown("---")
    
    for turma in turmas:
        # Suportar ambos os formatos: snake_case e camelCase
        horario_inicio = turma.get('horario_inicio') or turma.get('horarioInicio', '')
        horario_fim = turma.get('horario_fim') or turma.get('horarioFim', '')
        
        if horario_inicio and horario_fim:
            titulo = f"{turma['nome']} ({horario_inicio} as {horario_fim})"
        else:
            titulo = turma['nome']
        
        with st.expander(titulo):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if horario_inicio and horario_fim:
                    st.write(f"**Horario:** {horario_inicio} - {horario_fim}")
                else:
                    st.write(f"**Horario:** Nao definido")
                
                dias = turma.get('dias_semana', [])
                if dias:
                    dias_texto = ', '.join(dias)
                    st.write(f"**Dias:** {dias_texto}")
                
                if turma.get('descricao'):
                    st.write(f"**Descricao:** {turma['descricao']}")
                
                status = "Ativa" if turma.get('ativo', True) else "Inativa"
                st.write(f"**Status:** {status}")
            
            with col2:
                if turma.get('ativo', True):
                    if st.button("Desativar", key=f"desativar_{turma['id']}"):
                        turmas_service.atualizar_turma(turma['id'], {'ativo': False})
                        st.success("Turma desativada!")
                        st.rerun()
                else:
                    if st.button("Ativar", key=f"ativar_{turma['id']}"):
                        turmas_service.atualizar_turma(turma['id'], {'ativo': True})
                        st.success("Turma ativada!")
                        st.rerun()

def mostrar_formulario(turmas_service):
    st.markdown("### Cadastrar Nova Turma")
    
    with st.form("form_turma"):
        nome = st.text_input("Nome da Turma", placeholder="Ex: KIDS, ADULTA Matutino")
        
        col1, col2 = st.columns(2)
        with col1:
            horario_inicio = st.time_input("Horario de Inicio")
        with col2:
            horario_fim = st.time_input("Horario de Fim")
        
        st.markdown("**Dias da Semana:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            seg = st.checkbox("Seg")
        with col2:
            ter = st.checkbox("Ter")
        with col3:
            qua = st.checkbox("Qua")
        with col4:
            qui = st.checkbox("Qui")
        with col5:
            sex = st.checkbox("Sex")
        
        descricao = st.text_area("Descricao", placeholder="Informacoes adicionais sobre a turma")
        
        submitted = st.form_submit_button("Cadastrar Turma")
        
        if submitted:
            if not nome:
                st.error("Nome da turma e obrigatorio!")
                return
            
            dias_semana = []
            if seg: dias_semana.append("Segunda")
            if ter: dias_semana.append("Terca")
            if qua: dias_semana.append("Quarta")
            if qui: dias_semana.append("Quinta")
            if sex: dias_semana.append("Sexta")
            
            if not dias_semana:
                st.error("Selecione pelo menos um dia da semana!")
                return
            
            turma_data = {
                'nome': nome,
                'horario_inicio': horario_inicio.strftime("%H:%M"),
                'horario_fim': horario_fim.strftime("%H:%M"),
                'dias_semana': dias_semana,
                'descricao': descricao,
                'ativo': True
            }
            
            try:
                turmas_service.criar_turma(turma_data)
                st.success("Turma cadastrada com sucesso!")
                st.session_state.turmas_modo = 'lista'
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar turma: {str(e)}")