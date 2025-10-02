# IMPLEMENTACAO_MVP.md
Roteiro “pé no chão” — **Streamlit + Firestore + Auth interno (streamlit-authenticator)**

> Decisão: **não usaremos Google/Firebase Auth no MVP**.  
> Autenticação **interna** com `streamlit-authenticator` (usuários/senhas com **hash**), adequada para **uso interno** em time pequeno/controle de acesso básico.
> Para portal público/escala/SSO, planejar migração futura para Firebase Auth/IdP.

---

## 0) Preparação
**Segredos/variáveis**
- `FIREBASE_PROJECT_ID`
- `GOOGLE_APPLICATION_CREDENTIALS` → caminho do JSON da service account (Firestore)
- `streamlit-authenticator`:
  - Tabela de **usuários** em `secrets.toml` com **hash bcrypt** das senhas
  - Configuração de **cookie**: `name`, `key` (chave aleatória e secreta), `expiry_days`
  - Mapa de **papéis** (role) por usuário

**Ambientes**
- **Dev**: projeto Firestore de teste; usuários e senhas de desenvolvimento
- **Prod**: projeto Firestore dedicado; segredos separados; leis de acesso restrito ao time

**Segurança básica p/ produção (com streamlit-authenticator)**
- Executar **apenas via HTTPS** (Streamlit Cloud, reverse proxy com TLS, etc.)
- Guardar segredos em **secrets do provedor** (nunca comitar)
- **Hashes** de senha com `streamlit-authenticator` (bcrypt)
- **Cookie key** forte e rotacionável; `expiry_days` curto (ex.: 7)
- Limitar usuários (whitelist interna); processo de **troca de senha** documentado
- Logar acessos/erros (mínimo) e revisar periodicamente

---

## 1) Autenticação e Papéis (MVP)
- Login via `streamlit-authenticator` (usuário/senha), **sem Google**.
- Papel simplificado no MVP:
  - `admin` → acesso total (todas as páginas e ações)
- **Sem controle granular**: admin pode acessar tudo sem restrições.

---

## 2) Páginas (Streamlit)
**Home (KPIs) — por `ym` (“YYYY-MM”)**
- Receita do mês = **soma** `valor` onde `status == "pago"` e `ym == alvo`
- Inadimplência = **contagem** onde `status == "inadimplente"` e `exigivel == true`
- Ativos x Inativos = contagem em `/alunos`

**Alunos — listagem + CRUD**
- Campos mínimos: `nome`, `contato`, `vencimentoDia`, `status("ativo")`, `ativoDesde`
- Marcar **inativo** → `status="inativo"` e (opcional) `inativoDesde`

**Pagamentos — registrar mensal + extrato**
- **Upsert** em `/pagamentos/{alunoId_YYYY_MM}` com `ym`, `status`, `exigivel`, `alunoNome` (denormalizado), `paidAt` quando `status="pago"`
- Extrato por aluno: `where(alunoId==X) orderBy(ym desc) limit 24`

**Presenças — check-in + relatório**
- `addDoc` com `alunoId`, `data`, `ym`, `presente`
- Relatório mensal por `ym` (geral e por aluno)

**Graduação — subcoleção por aluno**
- `addDoc` com `nivel`, `data`, `obs`
- Timeline ordenada por `data`

**Planos — CRUD simples**
- `periodicidade="mensal"`, `valor`, `ativo` (e opcional `diaPadraoVencimento`)

---

## 3) Cache / Desempenho
- `st.cache_data(ttl=60)` nas leituras mais frequentes:
  - KPIs por `ym`
  - Lista de alunos
  - Pagamentos por mês
- Consultas **enxutas** por `ym`; **extratos** limitados (12–24 meses).
- Evitar leituras da coleção inteira; sempre `where(...)`/`order_by(...)`.

---

## 4) Critérios de Pronto (Definition of Done)
- **Pagamentos** usam **ID estável** `alunoId_YYYY_MM` (sem duplicidade).
- **KPIs** do mês conferem com os somatórios de consultas.
- **Autenticação** efetiva: acesso protegido por login admin.
- Fluxos operacionais (cadastrar aluno, registrar pagamento, marcar presença, registrar graduação) funcionam sem uso do console Firestore.

---

## 5) Testes manuais (essenciais)
**Alunos**
- Criar → listar → marcar inativo (checar `status`/`inativoDesde`).

**Pagamentos**
- `pago` → `paidAt` preenchido; aparece em receita do mês
- `inadimplente` → na lista de inadimplência do mês (`exigivel==true`)
- `ausente` → `exigivel=false` (cinza na UI; não afeta cobrança)

**Presenças**
- Check-in do dia → aparece no relatório (`ym` correto)

**Graduação**
- Inserir promoção → aparece ordenada por data na timeline

**Dashboard**
- KPIs corretas ao trocar `ym` (ex.: `2025-09` vs `2025-10`)

---

## 6) Operação e Observabilidade (mínimo)
- **Logs** de erro (apresentar mensagens claras ao usuário)
- **Backups** via export manual do Firestore (pós-MVP: job periódico)
- Checklist mensal: verificação de índices, revisão de acessos ao painel

---

## 7) Próximos passos (pós-MVP)
- Export CSV/Excel; alertas de vencimento; `/audits` (trilha de alterações); import XLSX
- Fortalecer autorização (papéis em coleção); eventualmente migrar para **Firebase Auth/SSO**
- Melhorar UX (filtros, busca), e performance (cache por usuário/período)