# CHECKLIST_KANBAN.md
Kanban orientado a tarefas — Sprints simuladas (MVP)

> Este arquivo é o **guia operacional** do agente.  
> Para cada item: marque `[x]` quando concluir, atualize **observações**.  
> Referência principal: `FIRESTORE_SCHEMA.md` e `IMPLEMENTACAO_MVP.md`.

---

## Sprint 0 — Preparação de Ambiente ✅ CONCLUÍDO
- [x] **S0-1** — Configurar projeto Streamlit (repo, virtualenv, dependências)
- [ ] **S0-2** — Service Account + variáveis (`GOOGLE_APPLICATION_CREDENTIALS`, `FIREBASE_PROJECT_ID`)
- [x] **S0-3** — Autenticação simples funcionando (login/logout)
- [x] **S0-4** — Definir **papel** inicial (somente admin)
- [ ] **S0-5** — Criar **índices** detalhados no Firestore: (ym), (alunoId,ym desc), (status,ym desc) em pagamentos; (status,nome) em alunos; (alunoId,ym desc), (ym) em presenças

**Evidências / Observações:**
✅ 2025-10-01: Estrutura completa, autenticação funcionando, commit inicial realizado
🔄 Próximo: Firebase setup para conectar com Firestore real

---

## Sprint 1 — Fundamentos de Domínio 🔄 EM ANDAMENTO
- [ ] **S1-0** — Conectar Firebase/Firestore real (service account + project setup)
- [ ] **S1-1** — Criar AlunosService (CRUD base + timestamps)
- [ ] **S1-2** — Página **Alunos** (listagem + formulário cadastro)
- [ ] **S1-3** — Editar aluno + marcar **inativo** (status + `inativoDesde`)
- [ ] **S1-4** — Criar PlanosService (CRUD base + timestamps)
- [ ] **S1-5** — Página **Planos** (CRUD simples para planos mensais)
- [ ] **S1-6** — Validação e testes de integração com Firestore

**Evidências / Observações:**
⏳ Prioridade: Firebase setup → Services → UI → Testes

**ORDEM DE EXECUÇÃO:**
1. **S1-0**: Firebase (base para tudo)
2. **S1-1**: AlunosService (lógica de negócio)
3. **S1-2**: UI Alunos (interface)
4. **S1-3**: Edição/Inativação (completar CRUD)
5. **S1-4**: PlanosService
6. **S1-5**: UI Planos
7. **S1-6**: Testes finais

---

## Sprint 2 — Financeiro Mensal
- [ ] **S2-1** — Registrar **pagamento mensal** (upsert em `/pagamentos/{alunoId_YYYY_MM}`)
- [ ] **S2-2** — **Extrato** por aluno (últimos 12–24 meses, `orderBy ym desc`)
- [ ] **S2-3** — Lista de **inadimplentes** do mês (`status="inadimplente"` & `exigivel=true`)
- [ ] **S2-4** — Tratar `ausente` com `exigivel=false` (cinza na UI)

**Evidências / Observações:**

---

## Sprint 3 — Operação de Dojo
- [ ] **S3-1** — **Presenças**: check-in por data (`ym`) e relatório mensal
- [ ] **S3-2** — **Graduação**: registrar promoção (subcoleção) e timeline por data
- [ ] **S3-3** — **Home/KPIs** por `ym`: receita do mês, inadimplência, ativos x inativos
- [ ] **S3-4** — **Cache** de leituras principais com `ttl=60`

**Evidências / Observações:**

---

## Sprint 4 — DoD + Qualidade
- [ ] **S4-1** — Verificação de **consistência**: pagamentos não duplicam; `paidAt` apenas em `pago`
- [ ] **S4-2** — **Autorização**: admin acessa tudo após login
- [ ] **S4-3** — **Performance**: consultas por `ym` e extratos limitados (≤24 meses)
- [ ] **S4-4** — **Usabilidade**: feedbacks (toast), mensagens de erro claras, validation inputs e forms
- [ ] **S4-5** — **Checklist de migração** (se necessário): mapeamento mínimo para import XLSX (pós-MVP)

**Evidências / Observações:**

---

---

## Sprint 0.5 — Autenticação interna e segurança mínima (streamlit-authenticator)
- [ ] **S0.5-1 — Hash de senhas (bcrypt):** gerar hashes com `streamlit-authenticator` e salvar em `secrets.toml` (nunca guardar senha em texto puro).
- [ ] **S0.5-2 — Cookie seguro:** definir `cookie.name`, `cookie.key` **forte/aleatória**, `expiry_days ≤ 7`.
- [ ] **S0.5-3 — HTTPS obrigatório:** garantir acesso apenas por HTTPS (Streamlit Cloud, ou reverse proxy com TLS).
- [ ] **S0.5-4 — Papel por usuário:** mapear `role=admin` por username em `secrets.toml`.
- [ ] **S0.5-5 — Guards por página/ação:** proteger acesso às páginas por login (admin acessa tudo).
- [ ] **S0.5-6 — Segredos protegidos:** manter `GOOGLE_APPLICATION_CREDENTIALS` e `FIREBASE_PROJECT_ID` apenas nos **secrets** do ambiente.
- [ ] **S0.5-7 — Sessão:** validar expiração e logout; revisar que o cookie expira corretamente.
- [ ] **S0.5-8 — Logs básicos:** registrar falhas de login e erros de acesso (sem dados sensíveis).
- [ ] **S0.5-9 — Revisão inicial:** checklist de quem tem acesso e rotação da `cookie.key` a cada trimestre.

**Evidências / Observações:**

---

## Sprint 2.5 — Qualidade de dados financeiro
- [ ] **S2.5-1 — ID estável de pagamentos:** confirmar `alunoId_YYYY_MM` em todos os fluxos de criação/edição.
- [ ] **S2.5-2 — `paidAt` somente em `pago`:** validar na camada de aplicação.
- [ ] **S2.5-3 — `exigivel=false` para ausente:** garantir que não entre na cobrança nem nos KPIs de receita.

**Evidências / Observações:**

---

## Sprint 4.5 — Hardening de Produção
- [ ] **S4.5-1 — Backup manual do Firestore:** script/ritual mensal (export).
- [ ] **S4.5-2 — Revisão de perfis:** quem é admin? remover usuários inativos.
- [ ] **S4.5-3 — Verificação de índices:** checar que as consultas por `ym`, `alunoId+ym desc`, `status+ym desc` estão com índices criados conforme FIRESTORE_SCHEMA.md.
- [ ] **S4.5-4 — Teste de latência:** tempo de carregamento de KPIs e listas (meta: <2s local/ <3s cloud).
- [ ] **S4.5-5 — Política de erros:** mensagens claras para usuário + log técnico resumido.

**Evidências / Observações:**

## Backlog (pós-MVP)
- [ ] Export CSV/Excel nas listas e relatórios
- [ ] Alerts (vencimentos), **/audits** para trilha de alterações
- [ ] Integração de pagamentos (boleto/cartão) e/ou lembretes automáticos
- [ ] Migrar auth para **Firebase Auth** (futuro) e implementar perfis múltiplos se necessário
- [ ] PWA/Portal do aluno (futuro React/Flutter) usando o mesmo Firestore