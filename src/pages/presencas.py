"""
Página de Presenças - Interface para check-ins e gestão de frequência
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.services.presencas_service import PresencasService
from src.services.alunos_service import AlunosService

def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'presencas_modo_selecionado' not in st.session_state:
        st.session_state.presencas_modo_selecionado = "Check-in Rápido"
    
    if 'presencas_aluno_selecionado' not in st.session_state:
        st.session_state.presencas_aluno_selecionado = None
    
    if 'presencas_data_selecionada' not in st.session_state:
        st.session_state.presencas_data_selecionada = date.today()
    
    if 'presencas_feedback_message' not in st.session_state:
        st.session_state.presencas_feedback_message = None
    
    if 'presencas_feedback_type' not in st.session_state:
        st.session_state.presencas_feedback_type = None

def criar_cards_estatisticas(stats: Dict[str, Any]):
    """Cria cards com estatísticas de presença"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Presenças",
            value=stats.get('total_presencas', 0),
            delta=f"+{stats.get('taxa_presenca', 0):.1f}% taxa"
        )
    
    with col2:
        st.metric(
            label="Total Faltas",
            value=stats.get('total_faltas', 0),
            delta=f"{stats.get('alunos_faltosos', 0)} alunos"
        )
    
    with col3:
        st.metric(
            label="Alunos Ativos",
            value=stats.get('alunos_ativos', 0),
            delta=f"{stats.get('dias_com_treino', 0)} dias de treino"
        )
    
    with col4:
        st.metric(
            label="Média/Dia",
            value=f"{stats.get('media_presencas_dia', 0):.1f}",
            delta=f"{stats.get('total_registros', 0)} registros"
        )

def criar_grafico_presencas_mes(presencas_por_dia: Dict[str, Dict[str, int]]):
    """Cria gráfico de presenças por dia do mês"""
    if not presencas_por_dia:
        st.info("Nenhum dado de presença disponível para exibir gráfico")
        return
    
    # Preparar dados para o gráfico
    datas = []
    presentes = []
    faltas = []
    
    for data, counts in sorted(presencas_por_dia.items()):
        datas.append(data)
        presentes.append(counts.get('presentes', 0))
        faltas.append(counts.get('faltas', 0))
    
    # Criar gráfico de barras empilhadas
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Presenças',
        x=datas,
        y=presentes,
        marker_color='green',
        text=presentes,
        textposition='inside'
    ))
    
    fig.add_trace(go.Bar(
        name='Faltas',
        x=datas,
        y=faltas,
        marker_color='red',
        text=faltas,
        textposition='inside'
    ))
    
    fig.update_layout(
        title='Presenças e Faltas por Dia',
        xaxis_title='Data',
        yaxis_title='Quantidade',
        barmode='stack',
        height=400
    )
    
    return fig

def exibir_checkin_rapido():
    """Interface para check-in rápido"""
    st.subheader("✅ Check-in Rápido")
    st.write("Marque presença rapidamente para a data de hoje")
    
    # Serviços
    presencas_service = PresencasService()
    alunos_service = AlunosService()
    
    # Buscar alunos ativos
    try:
        alunos = alunos_service.listar_alunos()
        if not alunos:
            st.warning("Nenhum aluno cadastrado. Cadastre alunos primeiro.")
            return
        
        # Ordenar por nome
        alunos.sort(key=lambda x: x.get('nome', ''))
        
        # Seleção de aluno
        col1, col2 = st.columns([2, 1])
        
        with col1:
            opcoes_alunos = [f"{aluno['nome']} ({aluno.get('graduacao', 'Sem graduação')})" 
                           for aluno in alunos]
            
            aluno_escolhido = st.selectbox(
                "Selecione o aluno:",
                options=opcoes_alunos,
                key="checkin_aluno_select"
            )
        
        with col2:
            data_checkin = st.date_input(
                "Data:",
                value=date.today(),
                key="checkin_data"
            )
        
        if aluno_escolhido:
            # Encontrar aluno selecionado
            indice_aluno = opcoes_alunos.index(aluno_escolhido)
            aluno = alunos[indice_aluno]
            
            # Verificar se já tem presença registrada na data
            presenca_existente = presencas_service.buscar_presenca_por_aluno_data(
                aluno['id'], data_checkin
            )
            
            # Exibir feedback persistente se houver
            if st.session_state.presencas_feedback_message:
                if st.session_state.presencas_feedback_type == "success":
                    st.success(st.session_state.presencas_feedback_message)
                elif st.session_state.presencas_feedback_type == "warning":
                    st.warning(st.session_state.presencas_feedback_message)
                elif st.session_state.presencas_feedback_type == "error":
                    st.error(st.session_state.presencas_feedback_message)
                
                # Botão para limpar feedback
                if st.button("✅ OK, entendi", key="clear_feedback"):
                    st.session_state.presencas_feedback_message = None
                    st.session_state.presencas_feedback_type = None
                    st.rerun()
            
            # Exibir status atual
            col1, col2, col3 = st.columns(3)
            
            if presenca_existente:
                status_atual = "PRESENTE" if presenca_existente.get('presente', False) else "AUSENTE"
                cor = "green" if presenca_existente.get('presente', False) else "red"
                
                with col1:
                    st.markdown(f"**Status atual:** :{cor}[{status_atual}]")
            else:
                with col1:
                    st.markdown("**Status atual:** Não registrado")
            
            # Botões de ação
            with col2:
                if st.button("✅ Marcar PRESENTE", key="btn_presente", type="primary"):
                    try:
                        resultado = presencas_service.registrar_presenca(
                            aluno['id'], data_checkin, presente=True
                        )
                        st.session_state.presencas_feedback_message = f"✅ {aluno['nome']} marcado como PRESENTE!"
                        st.session_state.presencas_feedback_type = "success"
                        st.rerun()
                    except Exception as e:
                        st.session_state.presencas_feedback_message = f"Erro ao registrar presença: {str(e)}"
                        st.session_state.presencas_feedback_type = "error"
                        st.rerun()
            
            with col3:
                if st.button("❌ Marcar AUSENTE", key="btn_ausente"):
                    try:
                        resultado = presencas_service.registrar_presenca(
                            aluno['id'], data_checkin, presente=False
                        )
                        st.session_state.presencas_feedback_message = f"❌ {aluno['nome']} marcado como AUSENTE"
                        st.session_state.presencas_feedback_type = "warning"
                        st.rerun()
                    except Exception as e:
                        st.session_state.presencas_feedback_message = f"Erro ao registrar falta: {str(e)}"
                        st.session_state.presencas_feedback_type = "error"
                        st.rerun()
            
            # Histórico recente do aluno
            with st.expander(f"📊 Histórico recente - {aluno['nome']}", expanded=False):
                try:
                    historico = presencas_service.obter_presencas_aluno(aluno['id'], limite_dias=10)
                    
                    if historico:
                        for presenca in historico:
                            data_presenca = presenca.get('data', '')
                            presente = presenca.get('presente', False)
                            icon = "✅" if presente else "❌"
                            status = "Presente" if presente else "Ausente"
                            
                            st.write(f"{icon} {data_presenca} - {status}")
                    else:
                        st.info("Nenhum histórico de presença encontrado")
                        
                except Exception as e:
                    st.error(f"Erro ao carregar histórico: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")

def exibir_lista_presencas():
    """Interface para visualizar lista de presenças"""
    st.subheader("📋 Lista de Presenças")
    
    presencas_service = PresencasService()
    alunos_service = AlunosService()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por mês
        mes_atual = date.today().strftime('%Y-%m')
        mes_filtro = st.text_input("Mês (YYYY-MM):", value=mes_atual, key="filtro_mes")
    
    with col2:
        # Filtro por status
        status_filtro = st.selectbox(
            "Status:",
            options=["Todos", "Apenas Presenças", "Apenas Faltas"],
            key="filtro_status"
        )
    
    with col3:
        limite = st.number_input("Limite de registros:", min_value=10, max_value=1000, value=100)
    
    # Buscar presenças
    try:
        filtros = {}
        if mes_filtro and mes_filtro.strip():
            filtros['ym'] = mes_filtro.strip()
        
        if status_filtro == "Apenas Presenças":
            filtros['presente'] = True
        elif status_filtro == "Apenas Faltas":
            filtros['presente'] = False
        
        presencas = presencas_service.listar_presencas(filtros=filtros, limite=limite)
        
        if not presencas:
            st.info("Nenhuma presença encontrada com os filtros aplicados")
            return
        
        # Buscar dados dos alunos para enrichment
        alunos = alunos_service.listar_alunos()
        alunos_dict = {aluno['id']: aluno for aluno in alunos}
        
        # Preparar dados para tabela
        dados_tabela = []
        for presenca in presencas:
            aluno_id = presenca.get('alunoId', '')
            aluno = alunos_dict.get(aluno_id, {'nome': 'Aluno não encontrado'})
            
            dados_tabela.append({
                'Data': presenca.get('data', ''),
                'Aluno': aluno.get('nome', 'Desconhecido'),
                'Graduação': aluno.get('graduacao', 'Sem graduação'),
                'Status': "✅ Presente" if presenca.get('presente', False) else "❌ Ausente",
                'Mês': presenca.get('ym', ''),
                'ID Presença': presenca.get('id', '')
            })
        
        # Exibir estatísticas
        total_presentes = len([p for p in presencas if p.get('presente', False)])
        total_faltas = len(presencas) - total_presentes
        taxa_presenca = (total_presentes / len(presencas)) * 100 if presencas else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Presenças", total_presentes)
        with col2:
            st.metric("Total Faltas", total_faltas)
        with col3:
            st.metric("Taxa de Presença", f"{taxa_presenca:.1f}%")
        
        # Exibir tabela
        if dados_tabela:
            df = pd.DataFrame(dados_tabela)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Botão para baixar CSV
            csv = df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"presencas_{mes_filtro}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Erro ao carregar presenças: {str(e)}")

def exibir_relatorio_mensal():
    """Interface para relatório mensal detalhado"""
    st.subheader("📊 Relatório Mensal")
    
    presencas_service = PresencasService()
    
    # Seleção do mês
    col1, col2 = st.columns([1, 1])
    
    with col1:
        mes_atual = date.today().strftime('%Y-%m')
        mes_relatorio = st.text_input("Mês para relatório (YYYY-MM):", value=mes_atual)
    
    with col2:
        if st.button("🔄 Gerar Relatório", type="primary"):
            st.session_state['gerar_relatorio'] = True
    
    if mes_relatorio and (st.session_state.get('gerar_relatorio', False) or 
                         st.session_state.get('relatorio_mes') == mes_relatorio):
        try:
            # Gerar relatório
            relatorio = presencas_service.obter_relatorio_mensal(mes_relatorio)
            st.session_state['relatorio_mes'] = mes_relatorio
            st.session_state['gerar_relatorio'] = False
            
            # Exibir cards de estatísticas
            criar_cards_estatisticas(relatorio)
            
            # Divisão em colunas para gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de presenças por dia
                fig_dias = criar_grafico_presencas_mes(relatorio.get('presencas_por_dia', {}))
                if fig_dias:
                    st.plotly_chart(fig_dias, use_container_width=True)
            
            with col2:
                # Gráfico de pizza - presença vs falta
                total_presencas = relatorio.get('total_presencas', 0)
                total_faltas = relatorio.get('total_faltas', 0)
                
                if total_presencas > 0 or total_faltas > 0:
                    fig_pizza = px.pie(
                        values=[total_presencas, total_faltas],
                        names=['Presenças', 'Faltas'],
                        title='Distribuição Presença/Falta',
                        color_discrete_map={'Presenças': 'green', 'Faltas': 'red'}
                    )
                    st.plotly_chart(fig_pizza, use_container_width=True)
            
            # Detalhes do relatório
            with st.expander("📋 Detalhes do Relatório", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Resumo Geral:**")
                    st.write(f"- Mês: {relatorio['ym']}")
                    st.write(f"- Total de registros: {relatorio['total_registros']}")
                    st.write(f"- Dias com treino: {relatorio['dias_com_treino']}")
                    st.write(f"- Alunos ativos: {relatorio['alunos_ativos']}")
                    st.write(f"- Média presença/dia: {relatorio['media_presencas_dia']}")
                    st.write(f"- Taxa de presença: {relatorio['taxa_presenca']:.1f}%")
                
                with col2:
                    st.write("**Estatísticas por Dia:**")
                    presencas_por_dia = relatorio.get('presencas_por_dia', {})
                    
                    if presencas_por_dia:
                        for data, counts in sorted(presencas_por_dia.items()):
                            total_dia = counts['presentes'] + counts['faltas']
                            st.write(f"- {data}: {counts['presentes']}P / {counts['faltas']}F (Total: {total_dia})")
                    else:
                        st.write("Nenhum dado disponível")
        
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

def exibir_frequencia_aluno():
    """Interface para análise de frequência individual"""
    st.subheader("👤 Frequência por Aluno")
    
    presencas_service = PresencasService()
    alunos_service = AlunosService()
    
    # Buscar alunos
    try:
        alunos = alunos_service.listar_alunos()
        if not alunos:
            st.warning("Nenhum aluno cadastrado")
            return
        
        alunos.sort(key=lambda x: x.get('nome', ''))
        
        # Seleção de aluno e mês
        col1, col2 = st.columns(2)
        
        with col1:
            opcoes_alunos = [f"{aluno['nome']} ({aluno.get('graduacao', 'Sem graduação')})" 
                           for aluno in alunos]
            
            aluno_escolhido = st.selectbox(
                "Selecione o aluno:",
                options=opcoes_alunos,
                key="freq_aluno_select"
            )
        
        with col2:
            mes_atual = date.today().strftime('%Y-%m')
            mes_freq = st.text_input("Mês (YYYY-MM):", value=mes_atual, key="freq_mes")
        
        if aluno_escolhido and mes_freq:
            # Encontrar aluno selecionado
            indice_aluno = opcoes_alunos.index(aluno_escolhido)
            aluno = alunos[indice_aluno]
            
            # Gerar relatório de frequência
            try:
                frequencia = presencas_service.obter_frequencia_aluno(aluno['id'], mes_freq)
                
                # Exibir métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Presenças", frequencia['total_presencas'])
                
                with col2:
                    st.metric("Total Faltas", frequencia['total_faltas'])
                
                with col3:
                    st.metric("Total Registros", frequencia['total_registros'])
                
                with col4:
                    taxa_cor = "normal"
                    if frequencia['taxa_presenca'] >= 80:
                        taxa_cor = "normal"
                    elif frequencia['taxa_presenca'] >= 60:
                        taxa_cor = "inverse"
                    else:
                        taxa_cor = "off"
                    
                    st.metric("Taxa de Presença", f"{frequencia['taxa_presenca']:.1f}%")
                
                # Detalhes dos dias
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Dias Presente:**")
                    dias_presente = frequencia.get('dias_presente', [])
                    if dias_presente:
                        for dia in sorted(dias_presente):
                            st.write(f"✅ {dia}")
                    else:
                        st.write("Nenhum dia presente registrado")
                
                with col2:
                    st.write("**Dias Ausente:**")
                    dias_ausente = frequencia.get('dias_ausente', [])
                    if dias_ausente:
                        for dia in sorted(dias_ausente):
                            st.write(f"❌ {dia}")
                    else:
                        st.write("Nenhuma falta registrada")
                
                # Gráfico de linha temporal
                if frequencia['total_registros'] > 0:
                    todas_datas = sorted(dias_presente + dias_ausente)
                    valores_presenca = []
                    
                    for data in todas_datas:
                        if data in dias_presente:
                            valores_presenca.append(1)  # Presente
                        else:
                            valores_presenca.append(0)  # Ausente
                    
                    if todas_datas:
                        fig_linha = go.Figure()
                        
                        fig_linha.add_trace(go.Scatter(
                            x=todas_datas,
                            y=valores_presenca,
                            mode='lines+markers',
                            name='Presença',
                            line=dict(color='green', width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig_linha.update_layout(
                            title=f'Timeline de Presença - {aluno["nome"]} ({mes_freq})',
                            xaxis_title='Data',
                            yaxis_title='Status (1=Presente, 0=Ausente)',
                            yaxis=dict(tickvals=[0, 1], ticktext=['Ausente', 'Presente']),
                            height=400
                        )
                        
                        st.plotly_chart(fig_linha, use_container_width=True)
            
            except Exception as e:
                st.error(f"Erro ao gerar frequência do aluno: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")

def show_presencas():
    """Função principal para exibir a página de presenças"""
    init_session_state()
    
    # Título da página
    st.title("✅ Gestão de Presenças")
    st.markdown("Sistema de check-in e controle de frequência dos alunos")
    
    # Navegação por abas
    modos = [
        "Check-in Rápido",
        "Lista de Presenças", 
        "Relatório Mensal",
        "Frequência por Aluno"
    ]
    
    modo_selecionado = st.selectbox(
        "Selecione o modo:",
        options=modos,
        index=modos.index(st.session_state.presencas_modo_selecionado),
        key="modo_presencas"
    )
    
    st.session_state.presencas_modo_selecionado = modo_selecionado
    
    # Linha divisória
    st.divider()
    
    # Exibir interface baseada no modo selecionado
    if modo_selecionado == "Check-in Rápido":
        exibir_checkin_rapido()
    
    elif modo_selecionado == "Lista de Presenças":
        exibir_lista_presencas()
    
    elif modo_selecionado == "Relatório Mensal":
        exibir_relatorio_mensal()
    
    elif modo_selecionado == "Frequência por Aluno":
        exibir_frequencia_aluno()
    
    # Rodapé
    st.markdown("---")
    st.markdown("💡 **Dica:** Use check-in rápido para presença diária e relatórios para análise de frequência")

def main():
    """Função principal da página de presenças"""
    show_presencas()

if __name__ == "__main__":
    main()