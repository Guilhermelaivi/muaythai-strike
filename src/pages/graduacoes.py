"""
Página de Graduações - Interface para gestão de graduações e promoções
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.services.graduacoes_service import GraduacoesService
from src.services.alunos_service import AlunosService

def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'graduacoes_modo_selecionado' not in st.session_state:
        st.session_state.graduacoes_modo_selecionado = "Registrar Graduação"
    
    if 'graduacoes_feedback_message' not in st.session_state:
        st.session_state.graduacoes_feedback_message = None
    
    if 'graduacoes_feedback_type' not in st.session_state:
        st.session_state.graduacoes_feedback_type = None

def exibir_registrar_graduacao():
    """Interface para registrar nova graduação"""
    st.subheader("🎓 Registrar Nova Graduação")
    st.write("Registre promoções e atualize graduações dos alunos")
    
    graduacoes_service = GraduacoesService()
    alunos_service = AlunosService()
    
    # Exibir feedback persistente se houver
    if st.session_state.graduacoes_feedback_message:
        if st.session_state.graduacoes_feedback_type == "success":
            st.success(st.session_state.graduacoes_feedback_message)
        elif st.session_state.graduacoes_feedback_type == "warning":
            st.warning(st.session_state.graduacoes_feedback_message)
        elif st.session_state.graduacoes_feedback_type == "error":
            st.error(st.session_state.graduacoes_feedback_message)
        
        # Botão para limpar feedback
        if st.button("✅ OK, entendi", key="clear_feedback_grad"):
            st.session_state.graduacoes_feedback_message = None
            st.session_state.graduacoes_feedback_type = None
            st.rerun()
    
    try:
        # Buscar alunos ativos
        alunos = alunos_service.listar_alunos()
        if not alunos:
            st.warning("Nenhum aluno cadastrado. Cadastre alunos primeiro.")
            return
        
        alunos.sort(key=lambda x: x.get('nome', ''))
        
        # Formulário de graduação
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção de aluno
            opcoes_alunos = [f"{aluno['nome']} ({aluno.get('graduacao', 'Sem graduação')})" 
                           for aluno in alunos]
            
            aluno_escolhido = st.selectbox(
                "Selecione o aluno:",
                options=opcoes_alunos,
                key="grad_aluno_select"
            )
            
            # Data da graduação
            data_graduacao = st.date_input(
                "Data da graduação:",
                value=date.today(),
                key="grad_data"
            )
        
        with col2:
            # Novo nível
            niveis_disponiveis = graduacoes_service.obter_niveis_graduacao_disponiveis()
            
            novo_nivel = st.selectbox(
                "Novo nível:",
                options=niveis_disponiveis,
                key="grad_nivel"
            )
            
            # Observações
            observacoes = st.text_area(
                "Observações (opcional):",
                placeholder="Ex: Exame realizado com excelência, destacou-se em katas...",
                key="grad_obs"
            )
        
        # Botão de registrar
        if st.button("🎓 Registrar Graduação", type="primary", key="btn_registrar_grad"):
            if aluno_escolhido and novo_nivel:
                try:
                    # Encontrar aluno selecionado
                    indice_aluno = opcoes_alunos.index(aluno_escolhido)
                    aluno = alunos[indice_aluno]
                    
                    # Registrar graduação
                    grad_id = graduacoes_service.registrar_graduacao(
                        aluno['id'], 
                        novo_nivel, 
                        data_graduacao,
                        observacoes if observacoes.strip() else None
                    )
                    
                    st.session_state.graduacoes_feedback_message = f"🎓 Graduação registrada com sucesso! {aluno['nome']} agora é {novo_nivel}"
                    st.session_state.graduacoes_feedback_type = "success"
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.graduacoes_feedback_message = f"Erro ao registrar graduação: {str(e)}"
                    st.session_state.graduacoes_feedback_type = "error"
                    st.rerun()
        
        # Candidatos à promoção
        st.markdown("---")
        st.subheader("📋 Candidatos à Promoção")
        
        try:
            candidatos = graduacoes_service.listar_candidatos_promocao()
            
            if candidatos:
                # Criar tabela de candidatos
                dados_candidatos = []
                for candidato in candidatos[:10]:  # Limitar a 10 para performance
                    dados_candidatos.append({
                        'Nome': candidato.get('nome', ''),
                        'Graduação Atual': candidato.get('graduacao_atual', ''),
                        'Última Graduação': candidato.get('data_ultima_graduacao', 'Nunca'),
                        'Meses desde última': candidato.get('meses_desde_ultima', 'N/A'),
                        'Total Graduações': candidato.get('total_graduacoes', 0)
                    })
                
                if dados_candidatos:
                    df_candidatos = pd.DataFrame(dados_candidatos)
                    st.dataframe(df_candidatos, width=800, hide_index=True)
            else:
                st.info("Nenhum candidato à promoção encontrado no momento.")
                
        except Exception as e:
            st.error(f"Erro ao buscar candidatos: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")

def exibir_timeline_aluno():
    """Interface para visualizar timeline de graduações de um aluno"""
    st.subheader("📈 Timeline de Graduações")
    
    graduacoes_service = GraduacoesService()
    alunos_service = AlunosService()
    
    try:
        # Buscar alunos
        alunos = alunos_service.listar_alunos()
        if not alunos:
            st.warning("Nenhum aluno cadastrado")
            return
        
        alunos.sort(key=lambda x: x.get('nome', ''))
        
        # Seleção de aluno
        opcoes_alunos = [f"{aluno['nome']} ({aluno.get('graduacao', 'Sem graduação')})" 
                       for aluno in alunos]
        
        aluno_escolhido = st.selectbox(
            "Selecione o aluno:",
            options=opcoes_alunos,
            key="timeline_aluno_select"
        )
        
        if aluno_escolhido:
            # Encontrar aluno selecionado
            indice_aluno = opcoes_alunos.index(aluno_escolhido)
            aluno = alunos[indice_aluno]
            
            # Obter timeline
            try:
                timeline = graduacoes_service.obter_timeline_aluno(aluno['id'])
                
                # Exibir estatísticas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Graduações", timeline['total_graduacoes'])
                
                with col2:
                    graduacao_atual = timeline.get('graduacao_atual')
                    nivel_atual = graduacao_atual.get('nivel', 'Sem graduação') if graduacao_atual else 'Sem graduação'
                    st.metric("Graduação Atual", nivel_atual)
                
                with col3:
                    primeira = timeline.get('primeira_graduacao')
                    data_primeira = primeira.get('data', 'N/A') if primeira else 'N/A'
                    st.metric("Primeira Graduação", data_primeira)
                
                with col4:
                    tempo_total = timeline.get('tempo_total_dias', 0)
                    anos = round(tempo_total / 365.25, 1) if tempo_total > 0 else 0
                    st.metric("Tempo Total", f"{anos} anos")
                
                # Timeline visual
                if timeline['timeline']:
                    st.markdown("---")
                    st.subheader("📊 Progressão de Graduações")
                    
                    # Gráfico de timeline
                    dados_timeline = []
                    for i, grad in enumerate(timeline['timeline']):
                        if grad:  # Verificar se grad não é None
                            dados_timeline.append({
                                'Data': grad.get('data', ''),
                                'Nível': grad.get('nivel', ''),
                                'Ordem': i + 1
                            })
                    
                    if dados_timeline:
                        df_timeline = pd.DataFrame(dados_timeline)
                        df_timeline['Data'] = pd.to_datetime(df_timeline['Data'])
                        
                        fig = px.line(
                            df_timeline, 
                            x='Data', 
                            y='Ordem',
                            title=f'Progressão de Graduações - {aluno["nome"]}',
                            markers=True
                        )
                        
                        # Adicionar anotações com os níveis
                        for i, row in df_timeline.iterrows():
                            fig.add_annotation(
                                x=row['Data'],
                                y=row['Ordem'],
                                text=row['Nível'],
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor="blue"
                            )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Detalhes da progressão
                if timeline['progressao']:
                    st.markdown("---")
                    st.subheader("⏱️ Análise de Progressão")
                    
                    for prog in timeline['progressao']:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**{prog['de']}** → **{prog['para']}**")
                        
                        with col2:
                            st.write(f"📅 {prog['data_inicial']} a {prog['data_final']}")
                        
                        with col3:
                            st.write(f"⏳ {prog['meses_aproximados']} meses ({prog['dias_entre']} dias)")
                
                # Histórico detalhado
                with st.expander("📋 Histórico Detalhado", expanded=False):
                    for grad in timeline['timeline']:
                        if grad:  # Verificar se grad não é None
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**{grad.get('nivel', '')}**")
                            
                            with col2:
                                st.write(f"📅 {grad.get('data', '')}")
                            
                            with col3:
                                obs = grad.get('obs', '')
                                st.write(f"📝 {obs}" if obs else "Sem observações")
                
            except Exception as e:
                st.error(f"Erro ao obter timeline: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")

def exibir_estatisticas_graduacoes():
    """Interface para estatísticas gerais de graduações"""
    st.subheader("📊 Estatísticas de Graduações")
    
    graduacoes_service = GraduacoesService()
    
    try:
        stats = graduacoes_service.obter_estatisticas_graduacoes()
        
        # Cards de estatísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alunos", stats['total_alunos'])
        
        with col2:
            st.metric("Alunos Graduados", stats['alunos_com_graduacoes'])
        
        with col3:
            st.metric("Total Promoções", stats['total_promocoes'])
        
        with col4:
            st.metric("Média Promoções/Aluno", f"{stats['media_promocoes_por_aluno']:.1f}")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por nível
            if stats['distribuicao_por_nivel']:
                fig_dist = px.pie(
                    values=list(stats['distribuicao_por_nivel'].values()),
                    names=list(stats['distribuicao_por_nivel'].keys()),
                    title='Distribuição por Graduação'
                )
                st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Taxa de alunos graduados
            graduados = stats['alunos_com_graduacoes']
            nao_graduados = stats['total_alunos'] - graduados
            
            if graduados > 0 or nao_graduados > 0:
                fig_taxa = px.pie(
                    values=[graduados, nao_graduados],
                    names=['Com Graduações', 'Sem Graduações'],
                    title='Taxa de Alunos Graduados',
                    color_discrete_map={'Com Graduações': 'green', 'Sem Graduações': 'red'}
                )
                st.plotly_chart(fig_taxa, use_container_width=True)
        
        # Detalhes
        with st.expander("📋 Detalhes das Estatísticas", expanded=False):
            st.write(f"**Taxa de alunos graduados:** {stats['taxa_alunos_graduados']:.1f}%")
            st.write(f"**Nível mais comum:** {stats['nivel_mais_comum']}")
            
            st.write("**Distribuição detalhada:**")
            for nivel, quantidade in stats['distribuicao_por_nivel'].items():
                porcentagem = (quantidade / stats['total_alunos']) * 100
                st.write(f"- {nivel}: {quantidade} alunos ({porcentagem:.1f}%)")
    
    except Exception as e:
        st.error(f"Erro ao obter estatísticas: {str(e)}")

def exibir_candidatos_promocao():
    """Interface para gerenciar candidatos à promoção"""
    st.subheader("🏆 Candidatos à Promoção")
    
    graduacoes_service = GraduacoesService()
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        meses_minimos = st.number_input(
            "Meses mínimos desde última graduação:",
            min_value=1,
            max_value=60,
            value=6,
            key="meses_minimos_filter"
        )
    
    try:
        filtros = {'meses_minimos_graduacao': meses_minimos}
        candidatos = graduacoes_service.listar_candidatos_promocao(filtros)
        
        if not candidatos:
            st.info("Nenhum candidato à promoção encontrado com os critérios atuais.")
            return
        
        st.write(f"**{len(candidatos)} candidatos encontrados**")
        
        # Tabela de candidatos
        dados_tabela = []
        for candidato in candidatos:
            dados_tabela.append({
                'Nome': candidato.get('nome', ''),
                'Graduação Atual': candidato.get('graduacao_atual', ''),
                'Última Graduação': candidato.get('data_ultima_graduacao', 'Nunca'),
                'Meses desde última': candidato.get('meses_desde_ultima', 'N/A'),
                'Dias desde última': candidato.get('dias_desde_ultima', 'N/A'),
                'Total Graduações': candidato.get('total_graduacoes', 0)
            })
        
        if dados_tabela:
            df_candidatos = pd.DataFrame(dados_tabela)
            
            # Exibir tabela
            st.dataframe(
                df_candidatos,
                width=1200,
                hide_index=True
            )
            
            # Botão para baixar CSV
            csv = df_candidatos.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"candidatos_promocao_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Erro ao carregar candidatos: {str(e)}")

def show_graduacoes():
    """Função principal para exibir a página de graduações"""
    init_session_state()
    
    # Título da página
    st.title("🎓 Gestão de Graduações")
    st.markdown("Sistema de promoções e controle de progressão dos alunos")
    
    # Navegação por abas
    modos = [
        "Registrar Graduação",
        "Timeline por Aluno",
        "Estatísticas Gerais",
        "Candidatos à Promoção"
    ]
    
    modo_selecionado = st.selectbox(
        "Selecione o modo:",
        options=modos,
        index=modos.index(st.session_state.graduacoes_modo_selecionado),
        key="modo_graduacoes"
    )
    
    st.session_state.graduacoes_modo_selecionado = modo_selecionado
    
    # Linha divisória
    st.divider()
    
    # Exibir interface baseada no modo selecionado
    if modo_selecionado == "Registrar Graduação":
        exibir_registrar_graduacao()
    
    elif modo_selecionado == "Timeline por Aluno":
        exibir_timeline_aluno()
    
    elif modo_selecionado == "Estatísticas Gerais":
        exibir_estatisticas_graduacoes()
    
    elif modo_selecionado == "Candidatos à Promoção":
        exibir_candidatos_promocao()
    
    # Rodapé
    st.markdown("---")
    st.markdown("💡 **Dica:** Use candidatos à promoção para identificar alunos prontos para avançar de graduação")

def main():
    """Função principal da página de graduações"""
    show_graduacoes()

if __name__ == "__main__":
    main()