# FIRESTORE_SCHEMA.md
Arquitetura de dados — MVP Academia Muay Thai (Streamlit + Firestore)

## Visão Geral
- Banco: **Firestore (NoSQL)**
- Padrões: `serverTimestamp` em todas as escritas; consultas por **`ym` ("YYYY-MM")** para recortes mensais.
- Cores são **só na UI**; no banco salvamos **status**.

---

## Coleções e Campos

### `/alunos/{alunoId}`
- `nome: string`
- `contato: { telefone?: string, email?: string }`
- `endereco?: string`
- `status: "ativo" | "inativo"`
- `vencimentoDia: number` (1–28)
- `ativoDesde: "YYYY-MM-DD"`
- `inativoDesde?: "YYYY-MM-DD"`
- `turma?: string`
- `ultimoPagamentoYm?: "YYYY-MM"`
- `createdAt, updatedAt: serverTimestamp`

#### Subcoleção `/alunos/{alunoId}/graduacoes/{gradId}`
- `nivel: string` (ex.: "Khan Amarelo")
- `data: "YYYY-MM-DD"`
- `obs?: string`
- `createdAt, updatedAt: serverTimestamp`

---

### `/planos/{planoId}`
- `nome: string`
- `periodicidade: "mensal"` (fixo no MVP)
- `valor: number`
- `ativo: boolean`
- `diaPadraoVencimento?: number`
- `createdAt, updatedAt: serverTimestamp`

---

### `/pagamentos/{alunoId_YYYY_MM}`  ← **ID estável**
- `alunoId: string`
- `alunoNome?: string` (denormalizado p/ listagens)
- `ano: number`
- `mes: number` (1–12)
- `ym: "YYYY-MM"`
- `valor: number`
- `status: "pago" | "inadimplente" | "ausente"`
- `exigivel: boolean` (se conta para cobrança; use `false` para cinza)
- `paidAt?: serverTimestamp` (quando `status=="pago"`)
- `createdAt, updatedAt: serverTimestamp`

**Regras de negócio (pagamentos):**
- **ID** = `alunoId_YYYY_MM` (evita duplicata; permite upsert com `merge:true`).
- `pago` → setar `paidAt`.
- `ausente` → considerar `exigivel=false` (não entra na cobrança).

---

### `/presencas/{presencaId}`
- `alunoId: string`
- `data: "YYYY-MM-DD"`
- `ym: "YYYY-MM"`
- `presente: boolean`
- `createdAt, updatedAt: serverTimestamp`

---

## Convenções & Enum
- `status` (financeiro): `"pago" | "inadimplente" | "ausente"`
- Cores na UI: **verde** (pago), **vermelho** (inadimplente), **cinza** (ausente/exigível=false).

---

## Índices Recomendados (mínimo)
- `pagamentos`:
  - (ym)
  - (alunoId, ym desc)
  - (status, ym desc)
- `alunos`: (status, nome)
- `presencas`:
  - (alunoId, ym desc)
  - (ym)

> Observação: crie índices sob demanda quando o Firestore sugerir, mas estes cobrem os fluxos do MVP.

---

## Notas de Integridade
- **Timestamps:** sempre `createdAt` e `updatedAt` com `serverTimestamp`.
- **Denormalizações:** use apenas para UI (ex.: `alunoNome` em pagamentos).
- **Limpeza:** archive alunos inativos, não delete pagamentos.