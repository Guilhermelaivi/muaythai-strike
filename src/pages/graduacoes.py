import streamlit as st
from datetime import date
import pandas as pd
from src.services.graduacoes_service import GraduacoesService
from src.services.alunos_service import AlunosService
from src.services.turmas_service import TurmasService
from src.utils.cache_service import CacheManager


def exibir_registrar_graduacao():
    # Reusar instâncias via session_state (T25)
    if 'graduacoes_service' not in st.session_state:
        st.session_state.graduacoes_service = GraduacoesService()
    if 'alunos_service' not in st.session_state:
        st.session_state.alunos_service = AlunosService()
    if 'turmas_service' not in st.session_state:
        st.session_state.turmas_service = TurmasService()
    graduacoes_service = st.session_state.graduacoes_service
    alunos_service = st.session_state.alunos_service
    turmas_service = st.session_state.turmas_service
    cache_manager = CacheManager()

    try:
        # Filtro por turma
        turmas = turmas_service.listar_turmas(apenas_ativas=True)
        if not turmas:
            st.warning("⚠️ Nenhuma turma cadastrada no sistema.")
            return

        opcoes_turmas = [f"{t.get('nome', 'Sem nome')} ({t.get('horarioInicio', '')} - {t.get('horarioFim', '')})" for t in turmas]
        turma_map = {opcoes_turmas[i]: turmas[i] for i in range(len(turmas))}

        col_filtro, col_nivel = st.columns(2)

        with col_filtro:
            turma_filtro = st.selectbox(
                "🏫 Filtrar por Turma",
                options=opcoes_turmas,
                key="grad_turma_filtro"
            )

        # Carregar e filtrar alunos
        todos_alunos = cache_manager.get_alunos_cached(alunos_service)
        if not todos_alunos:
            st.warning("Nenhum aluno cadastrado. Cadastre alunos primeiro.")
            return

        turma_obj = turma_map[turma_filtro]
        turma_nome = turma_obj.get('nome', '')
        alunos = [a for a in todos_alunos if a.get('turma', '') == turma_nome]

        if not alunos:
            st.info("ℹ️ Nenhum aluno encontrado para esta turma.")
            return

        alunos.sort(key=lambda x: x.get('nome', ''))

        niveis_disponiveis = graduacoes_service.obter_niveis_graduacao_disponiveis()

        with col_nivel:
            novo_nivel = st.selectbox(
                "Novo nível",
                options=niveis_disponiveis,
                key="grad_nivel"
            )

        col_data, col_obs = st.columns(2)
        with col_data:
            data_graduacao = st.date_input(
                "Data da graduação:",
                value=date.today(),
                min_value=date(2026, 1, 1) if st.session_state.get('data_mode', 'operacional') == 'operacional' else date(2024, 1, 1),
                key="grad_data",
                format="DD/MM/YYYY"
            )
        with col_obs:
            observacoes = st.text_area(
                "Observações:",
                placeholder="Ex: Exame realizado com excelência",
                key="grad_obs",
                height=68
            )

        st.divider()

        # Seleção batch de alunos com checkboxes
        st.subheader(f"📋 Selecionar Alunos ({len(alunos)})")

        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            if st.button("✅ Selecionar Todos", key="grad_sel_all", use_container_width=True):
                for aluno in alunos:
                    st.session_state[f"grad_chk_{aluno['id']}"] = True
                st.rerun()
        with col_sel2:
            if st.button("❌ Limpar Seleção", key="grad_sel_none", use_container_width=True):
                for aluno in alunos:
                    st.session_state[f"grad_chk_{aluno['id']}"] = False
                st.rerun()

        selecionados = []
        for aluno in alunos:
            checked = st.checkbox(
                f"**{aluno.get('nome', 'N/A')}** — {aluno.get('graduacao', 'Sem graduação')}",
                key=f"grad_chk_{aluno['id']}",
                value=st.session_state.get(f"grad_chk_{aluno['id']}", False)
            )
            if checked:
                selecionados.append(aluno)

        st.divider()

        qtd = len(selecionados)
        label_btn = f"🥋 Promover {qtd} aluno{'s' if qtd != 1 else ''} para {novo_nivel}" if qtd else "🥋 Selecione alunos acima"

        if st.button(label_btn, type="primary", disabled=qtd == 0, key="btn_registrar_grad_batch"):
            sucesso = 0
            erros = []
            for aluno in selecionados:
                try:
                    graduacoes_service.registrar_graduacao(
                        aluno['id'],
                        novo_nivel,
                        data_graduacao,
                        observacoes.strip() if observacoes and observacoes.strip() else None
                    )
                    sucesso += 1
                except Exception as e:
                    erros.append(f"{aluno.get('nome', '?')}: {e}")

            if sucesso:
                st.toast(f"✅ {sucesso} graduação(ões) registrada(s) → {novo_nivel}")
            if erros:
                st.toast(f"⚠️ {len(erros)} erro(s): {'; '.join(erros)}")

            # Limpar checkboxes
            for aluno in alunos:
                st.session_state.pop(f"grad_chk_{aluno['id']}", None)
            st.rerun()

    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")


def show_graduacoes():
    st.title("🥋 Registrar Graduação")
    st.markdown("Selecione alunos e promova em lote")
    st.divider()
    exibir_registrar_graduacao()


def main():
    show_graduacoes()


if __name__ == "__main__":
    main()
