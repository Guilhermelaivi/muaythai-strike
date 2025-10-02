# DIAGRAMAS_SEQUENCIA_MVP.md
Sequência dos principais fluxos do MVP — **Streamlit + Firestore**  
Cada diagrama foi separado por contexto para facilitar revisão e evolução.

> Observação: sem pagamento trimestral neste MVP. Somente **mensal**.

---

## 1) Autenticação (streamlit-authenticator, sem Google)
```mermaid
sequenceDiagram
  autonumber
  actor User as Usuário
  participant UI as Streamlit UI (Login)
  participant Auth as streamlit-authenticator
  participant Secrets as secrets.toml (users, hashes, roles, cookie)
  participant Session as Sessão

  User->>UI: Abre app / insere usuário e senha
  UI->>Secrets: carrega config (hashes, cookie, roles)
  UI->>Auth: login(username, password, cookie-config)
  alt credenciais válidas
    Auth-->>UI: ok (name, username)
    UI->>Secrets: obter papel do usuário
    Secrets-->>UI: role (admin)
    UI->>Session: salvar sessão (user, role, expiry)
    UI-->>User: Redireciona para Dashboard
  else falha
    Auth-->>UI: erro (inválido)
    UI-->>User: Mensagem de erro
  end
```
```mermaid
sequenceDiagram
  autonumber
  actor User as Usuário
  participant UI as Streamlit UI (Login)
  participant Auth as streamlit-authenticator
  participant Roles as Papéis (config)
  participant Session as Sessão

  User->>UI: Abre app / clica "Entrar"
  UI->>Auth: login(username, password)
  alt credenciais válidas
    Auth-->>UI: ok (nome, username)
    UI->>Roles: obter papel do usuário
    Roles-->>UI: admin
    UI->>Session: salvar sessão (user, role)
    UI-->>User: Redireciona para Dashboard
  else falha
    Auth-->>UI: erro (inválido)
    UI-->>User: Mensagem de erro
  end
```

---

## 2) Cadastro de Aluno
```mermaid
sequenceDiagram
  autonumber
  actor Gestor as Gestor/Professor
  participant UI as Streamlit UI (Form Aluno)
  participant AlunosSvc as alunosService
  participant FS as Firestore (alunos)

  Gestor->>UI: Preenche formulário (nome, contato, vencimentoDia...)
  UI->>AlunosSvc: onSubmit(formData)
  note right of AlunosSvc: payload {nome, contato, status:"ativo", vencimentoDia, ativoDesde, createdAt, updatedAt}
  AlunosSvc->>FS: addDoc("alunos", payload)
  FS-->>AlunosSvc: docRef (alunoId)
  AlunosSvc-->>UI: sucesso (toast) + limpar formulário
  UI-->>Gestor: Lista de alunos atualizada
```

---

## 3) Planos (CRUD)
```mermaid
sequenceDiagram
  autonumber
  actor User as Usuário
  participant UI as Streamlit UI (Planos)
  participant PlanosSvc as planosService
  participant FS as Firestore (planos)

  User->>UI: Criar/editar plano (mensal, valor, dia padrão)
  UI->>PlanosSvc: salvarPlano({nome, periodicidade:"mensal", valor})
  PlanosSvc->>FS: add/set/update("planos", {...})
  FS-->>PlanosSvc: ok
  PlanosSvc-->>UI: sucesso / lista atualizada
```

---

## 4) Pagamento Mensal (ID estável + ym)
```mermaid
sequenceDiagram
  autonumber
  actor Financeiro as Financeiro
  participant UI as Streamlit UI (Registrar Pagamento)
  participant PgtoSvc as pagamentosService
  participant FS as Firestore (pagamentos)

  Financeiro->>UI: Seleciona aluno, ano, mês, valor
  UI->>PgtoSvc: registrarPagamento({alunoId, alunoNome, ano, mes, valor, status:"pago"})
  note right of PgtoSvc: ym = "YYYY-MM"; docId = "alunoId_YYYY_MM"; alunoNome denormalizado p/ listagens
  PgtoSvc->>FS: setDoc("pagamentos/docId", {alunoId, alunoNome, ano, mes, ym, valor, status:"pago", exigivel:true, paidAt:serverTs, createdAt, updatedAt}, {merge:true})
  FS-->>PgtoSvc: ok
  PgtoSvc-->>UI: sucesso / atualizar extrato (orderBy ym desc)
```

---

## 5) Presenças (Check-in)
```mermaid
sequenceDiagram
  autonumber
  actor Professor as Professor
  participant UI as Streamlit UI (Check-in)
  participant PresSvc as presencasService
  participant FS as Firestore (presencas)

  Professor->>UI: Marca presença na data
  UI->>PresSvc: salvarPresenca({alunoId, data:"YYYY-MM-DD", ym:"YYYY-MM", presente:true})
  PresSvc->>FS: addDoc("presencas", {alunoId, data, ym, presente})
  FS-->>PresSvc: ok
  PresSvc-->>UI: sucesso / relatório do mês (where ym)
```

---

## 6) Graduação (Subcoleção do Aluno)
```mermaid
sequenceDiagram
  autonumber
  actor Professor as Professor
  participant UI as Streamlit UI (Graduação)
  participant GradSvc as graduacoesService
  participant FS as Firestore (alunos/{id}/graduacoes)

  Professor->>UI: Registra promoção (nível, data, obs)
  UI->>GradSvc: addGraduacao(alunoId, {nivel, data, obs})
  GradSvc->>FS: addDoc("alunos/alunoId/graduacoes", {nivel, data, obs})
  FS-->>GradSvc: ok
  GradSvc-->>UI: sucesso / timeline ordenada
```

---

## 7) Dashboard (KPIs por ym)
```mermaid
sequenceDiagram
  autonumber
  actor Gestor as Gestor
  participant UI as Streamlit UI (Dashboard)
  participant DashSvc as dashboardService
  participant FS_P as Firestore (pagamentos)
  participant FS_A as Firestore (alunos)

  Gestor->>UI: Abre dashboard (mês corrente)
  UI->>DashSvc: carregarKPIs(ym)
  par Receita do mês
    DashSvc->>FS_P: query pagamentos where ym=={ym} and status in ["pago"]
    FS_P-->>DashSvc: docs → somar valor
  and Inadimplência
    DashSvc->>FS_P: query pagamentos where ym=={ym} and status=="inadimplente" and exigivel==true
    FS_P-->>DashSvc: docs → contar
  and Ativos x Inativos
    DashSvc->>FS_A: query alunos where status in ["ativo","inativo"]
    FS_A-->>DashSvc: docs → contagem/%
  end
  DashSvc-->>UI: KPIs (cards + gráficos)
```