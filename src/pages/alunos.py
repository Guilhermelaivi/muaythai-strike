"""
Página de Alunos - CRUD e gerenciamento
"""

import streamlit as st

def show_alunos():
    """Exibe a página de gerenciamento de alunos"""
    
    st.markdown("## 👥 Gerenciamento de Alunos")
    
    # Placeholder para Sprint 1
    st.info("🚧 **Sprint 1** - Esta página será implementada na próxima sprint")
    
    st.markdown("""
    ### 📋 Funcionalidades planejadas:
    - ✅ Lista de alunos com filtros
    - ✅ Cadastro de novos alunos
    - ✅ Edição de dados dos alunos
    - ✅ Marcar aluno como inativo
    - ✅ Visualização de histórico
    """)
    
    # Mock de estrutura
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📊 Lista de Alunos")
        st.dataframe({
            'Nome': ['João Silva', 'Maria Santos', 'Pedro Costa'],
            'Status': ['Ativo', 'Ativo', 'Inativo'],
            'Vencimento': ['Dia 05', 'Dia 15', 'Dia 10'],
            'Última Graduação': ['Khan Amarelo', 'Khan Branco', 'Khan Azul']
        })
    
    with col2:
        st.markdown("#### ➕ Ações")
        if st.button("Novo Aluno", type="primary"):
            st.success("Em desenvolvimento...")
        if st.button("Filtrar"):
            st.info("Filtros em desenvolvimento...")