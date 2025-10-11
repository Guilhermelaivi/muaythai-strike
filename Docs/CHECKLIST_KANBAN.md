# CHECKLIST_KANBAN.md
Kanban orientado a tarefas — Sprints simuladas (MVP)

> Este a**TODOS OS OBJETIVOS ATINGIDOS - PRONTO PARA SPRINT 5**

---

## Sprint 5 — Deploy e Usabilidade 🚀 EM ANDAMENTO
- [ ] **S5-1** — **Preparação GitHub**: README.md profissional, .gitignore, estrutura limpa
- [ ] **S5-2** — **Requirements.txt**: Dependências atualizadas e pinned para deploy
- [ ] **S5-3** — **Configuração Deploy**: Preparar para Vercel/Render/Railway (gratuito)
- [ ] **S5-4** — **Variáveis de Ambiente**: Documentar setup Firebase para produção
- [ ] **S5-5** — **Validações Frontend**: Melhorar UX com validações em tempo real
- [ ] **S5-6** — **Feedback Visual**: Loading states, confirmações, mensagens de sucesso
- [ ] **S5-7** — **Responsividade**: Garantir funcionamento em mobile/tablet
- [ ] **S5-8** — **Documentação**: Guia de instalação e uso para o dono da academia

**Evidências / Observações:**

---

## Sprint 4 — DoD + Qualidadeo é o **guia operacional** do agente.  
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

## Sprint 1 — Fundamentos de Domínio ✅ CONCLUÍDO
- [x] **S1-0** — Conectar Firebase/Firestore real (service account + project setup)
- [x] **S1-1** — Criar AlunosService (CRUD base + timestamps)
- [x] **S1-2** — Página **Alunos** (listagem + formulário cadastro)
- [x] **S1-3** — Editar aluno + marcar **inativo** (status + `inativoDesde`)
- [x] **S1-4** — Criar PlanosService (CRUD base + timestamps)
- [x] **S1-5** — Página **Planos** (CRUD simples para planos mensais)
- [x] **S1-6** — Validação e testes de integração com Firestore

**Evidências / Observações:**
✅ 2025-10-01: Sprint 1 CONCLUÍDA COM SUCESSO TOTAL!
- 🔥 Firebase projeto 'strikethai' conectado e operacional
- 👥 AlunosService: CRUD completo + validações + timestamps automáticos
- 💰 PlanosService: CRUD completo + estatísticas + análise de valores
- 🎨 UI Alunos: Interface completa (lista, cadastro, edição, busca, stats)
- 🎨 UI Planos: Interface completa (lista, cadastro, edição, busca, stats)
- 🧪 Testes realizados: Todos os critérios validados e aprovados
- 🌐 MVP operacional: http://localhost:8501 (admin/admin123)
- 📊 Dados reais: 8 alunos, 4 planos cadastrados no Firestore

**TODOS OS OBJETIVOS ATINGIDOS - PRONTO PARA SPRINT 2**

---

## Sprint 2 — Sistema de Pagamentos ✅ CONCLUÍDO
- [x] **S2-1** — Criar PagamentosService (Firestore collection `/pagamentos/{alunoId_YYYY_MM}`)
- [x] **S2-2** — Página **Pagamentos** — registrar mensalidade paga
- [x] **S2-3** — Extrato detalhado por aluno (histórico de pagtos + faltas)
- [x] **S2-4** — Lista de inadimplentes (filtros por mês/ano)
- [x] **S2-5** — Notificação automática ausentes (>7 dias sem treino)

**Evidências / Observações:**
✅ 2025-10-01: Sprint 2 CONCLUÍDA COM SUCESSO TOTAL!
- 💳 PagamentosService: CRUD completo + ID estável alunoId_YYYY_MM
- 🎯 Schema seguido: status (pago/inadimplente/ausente), exigivel, timestamps
- 💰 Página Pagamentos: Interface completa (lista, cadastro, inadimplentes, stats)
- 📊 Extrato por aluno: Histórico de 12 meses com método obter_extrato_aluno()
- 🚫 Lista inadimplentes: Filtros por mês + ações rápidas de pagamento
- 🚨 Sistema de notificações: NotificationService + alertas no Dashboard
- 📈 Estatísticas: Receita, taxa inadimplência, distribuição por status
- 🎨 UI integrada: Menu navegação + padrão consistente das outras páginas

**TODOS OS OBJETIVOS ATINGIDOS - PRONTO PARA SPRINT 3**

---

## Sprint 3 — Operação de Dojo ✅ CONCLUÍDO
- [x] **S3-1** — **Presenças**: check-in por data (`ym`) e relatório mensal
- [x] **S3-2** — **Graduação**: registrar promoção (subcoleção) e timeline por data
- [x] **S3-3** — **Home/KPIs** por `ym`: receita do mês, inadimplência, ativos x inativos
- [x] **S3-4** — **Cache** de leituras principais com `ttl=60`

**Evidências / Observações:**
✅ 2025-10-02: Sprint 3 CONCLUÍDA COM SUCESSO TOTAL!
- ✅ PresencasService: Sistema completo de check-in com relatórios mensais por ym
- 🥋 GraduacoesService: Subcoleção funcional + timeline + estatísticas + candidatos
- 📊 Dashboard KPIs: Métricas reais por mês (receita, inadimplência, alunos ativos)
- ⚡ CacheService: Sistema implementado com TTL=60s + invalidação inteligente
- 🎨 UI integrada: Todas as páginas funcionais com CRUD completo
- 🐛 Correções: Timeline graduações (NoneType), edição pagamentos, navegação
- 🧹 Interface limpa: Botões cache removidos, ações rápidas simplificadas

**TODOS OS OBJETIVOS ATINGIDOS - PRONTO PARA SPRINT 5**

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
- [ ] **Search na lista de pagamentos**: Campo de busca para filtrar pagamentos por nome do aluno na listagem principal
- [ ] **Histórico por aluno otimizado**: Ao clicar em um aluno, carregar apenas seus pagamentos históricos (não toda a lista) 
- [ ] Alerts (vencimentos), **/audits** para trilha de alterações
- [ ] Integração de pagamentos (boleto/cartão) e/ou lembretes automáticos
- [ ] Migrar auth para **Firebase Auth** (futuro) e implementar perfis múltiplos se necessário
- [ ] PWA/Portal do aluno (futuro React/Flutter) usando o mesmo Firestore