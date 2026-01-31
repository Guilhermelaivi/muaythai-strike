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
- `dataNascimento?: "YYYY-MM-DD"` (data de nascimento do aluno)
- `status: "ativo" | "inativo"`
- `vencimentoDia: number` (1–28)
- `ativoDesde: "YYYY-MM-DD"`
- `inativoDesde?: "YYYY-MM-DD"`
- `turma?: string`
- `ultimoPagamentoYm?: "YYYY-MM"`
- `responsavel?: { nome?: string, telefone?: string, cpf?: string, rg?: string, dataNascimento?: "YYYY-MM-DD" }`
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
- `status: "pago" | "devedor" | "inadimplente" | "ausente"`
- `dataVencimento: 10 | 15 | 25` (dia do vencimento no mês)
- `carenciaDias: number` (padrão: 0 - sem carência, 1 dia após = inadimplente)
- `dataAtraso?: "YYYY-MM-DD"` (calculada - quando vira inadimplente)
- `exigivel: boolean` (DEPRECATED - usar status ao invés)
- `paidAt?: serverTimestamp` (quando `status=="pago"`)
- `createdAt, updatedAt: serverTimestamp`

**Regras de negócio (pagamentos):**
- **ID** = `alunoId_YYYY_MM` (evita duplicata; permite upsert com `merge:true`).
- **Vencimentos válidos**: Apenas dia 10, 15 ou 25 do mês
- **Status Devedor** (🔔 A Cobrar): 
  - Alerta para gestão ~10 dias ANTES do vencimento
  - Vencimento dia 10 → alerta dia 01 (9 dias antes)
  - Vencimento dia 15 → alerta dia 05 (10 dias antes)
  - Vencimento dia 25 → alerta dia 15 (10 dias antes)
- **Status Inadimplente** (🔴 Em Atraso):
  - SEM carência - passou 1 dia do vencimento = inadimplente
- **Status Pago**: setar `paidAt` com timestamp
- **Status Ausente**: considerar `exigivel=false` (não entra na cobrança)

---

### `/presencas/{presencaId}`
- `alunoId: string`
- `data: "YYYY-MM-DD"`
- `ym: "YYYY-MM"`
- `presente: boolean`
- `createdAt, updatedAt: serverTimestamp`

---

## Convenções & Enum
- `status` (financeiro): `"pago" | "devedor" | "inadimplente" | "ausente"`
- Cores na UI: 
  - **🟢 Verde** (pago) - Pagamento confirmado
  - **🔔 Amarelo** (devedor) - A cobrar (alerta para gestão)
  - **🔴 Vermelho** (inadimplente) - Em atraso
  - **⚪ Cinza** (ausente) - Não exigível

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