# 🎯 RESUMO EXECUTIVO - Validação de Requisitos

**Sistema:** Spirit Muay thai - MVP Muay Thai  
**Data:** 20/11/2025  
**Status:** ⚠️ AGUARDANDO VALIDAÇÃO CLIENTE

---

## 🔴 DECISÕES URGENTES NECESSÁRIAS

### 1️⃣ Sistema de Pagamentos - Regras de Vencimento

**Implementação Atual:**
```
Vencimentos permitidos: Apenas dia 10, 15 ou 25
Carência inadimplência: 3 dias após vencimento
Alerta de cobrança: ~10 dias ANTES do vencimento

Exemplo (Vencimento dia 15):
├─ Dia 01-04: Pendente (não cobra)
├─ Dia 05-15: DEVEDOR 🔔 (a cobrar)
├─ Dia 16-17: DEVEDOR (dentro carência)
└─ Dia 18+:   INADIMPLENTE 🔴 (em atraso)
```

**❓ PERGUNTAS:**
- ✅ Estes 3 dias de vencimento (10/15/25) estão corretos?
- ✅ Alertar 10 dias ANTES faz sentido operacionalmente?
- ✅ 3 dias de carência é adequado ou muito curto?

---

### 2️⃣ Nomenclatura - Cliente Entende?

**Termos Técnicos Usados:**
- 🔔 **DEVEDOR** = Período de cobrança (ainda não venceu)
- 🔴 **INADIMPLENTE** = Em atraso (venceu + carência)

**❓ VALIDAR:**
- ✅ Termo "devedor" faz sentido ou confunde?
- ✅ Seria melhor "A Vencer", "Próximo ao Vencimento"?
- ✅ "Inadimplente" é muito forte? Usar "Atrasado"?

---

### 3️⃣ Aluno Ausente - Regra de Cobrança

**Situação:**
- Aluno faltou o mês inteiro → Status "ausente"

**❓ DECIDIR:**
- ✅ Aluno ausente PAGA a mensalidade?
  - [ ] SIM → Cobra normalmente
  - [ ] NÃO → Isenta de pagamento
  - [ ] DEPENDE → Ausência justificada vs não justificada

---

### 4️⃣ Menores de Idade - Responsável Legal

**Atual:** Campo responsável existe mas não é obrigatório

**❓ VALIDAR:**
- ✅ Menor (<18 anos) DEVE ter responsável cadastrado?
- ✅ Validar CPF do responsável?
- ✅ Precisa termo de responsabilidade assinado?
- ✅ Turma KIDS deve exigir automaticamente?

---

### 5️⃣ Geração de Pagamentos - Manual ou Automática?

**❓ ESCLARECER FLUXO:**

**Opção A - Automático:**
```
Todo dia 1º do mês:
├─ Sistema gera pagamento para TODOS alunos ativos
├─ Status inicial: "devedor" (se hoje >= dia cobrança)
└─ Secretária só marca como "pago" quando receber
```

**Opção B - Manual:**
```
Secretária cadastra pagamento quando aluno paga
├─ Cria registro com status "pago"
└─ Não há cobrança automática
```

**Opção C - Híbrido:**
```
Sistema gera automaticamente MAS
├─ Secretária pode ajustar antes de "confirmar" o mês
└─ Pode marcar ausentes, isenções, etc.
```

- ✅ Qual opção desejada?

---

## 🐛 BUGS CRÍTICOS IDENTIFICADOS

### BUG #1: NotificationService - Cálculo de Atraso ERRADO
**Problema:** Assume sempre vencimento dia 15, ignora campo real  
**Impacto:** Cálculo de dias de atraso INCORRETO  
**Severidade:** 🔴 CRÍTICA  
**Correção:** Usar `pagamento.dataVencimento` + `carenciaDias`

### BUG #2: Dashboard - Métrica "Inadimplentes" Ambígua
**Problema:** Não separa "A Cobrar" de "Em Atraso"  
**Impacto:** Informação confusa para gestão  
**Severidade:** 🟡 MÉDIA  
**Correção:** Mostrar 2 métricas separadas

### BUG #3: Formulário Pagamento - Falta opção "devedor"
**Problema:** Não permite criar pagamento manual como "devedor"  
**Impacto:** Inconsistência com sistema automático  
**Severidade:** 🟡 MÉDIA  
**Correção:** Adicionar opção OU ocultar campo status

---

## 📚 DOCUMENTAÇÃO DESATUALIZADA

**FIRESTORE_SCHEMA.md:**
```diff
❌ Atual:
- status: "pago" | "inadimplente" | "ausente"

✅ Deve ser:
- status: "pago" | "devedor" | "inadimplente" | "ausente"
+ dataVencimento: 10 | 15 | 25
+ carenciaDias: number (padrão: 3)
+ dataAtraso: "YYYY-MM-DD" (calculada)
```

**Ação:** Atualizar antes de próximo commit

---

## ✅ O QUE ESTÁ FUNCIONANDO BEM

| Módulo | Status | Nota |
|--------|--------|------|
| 👥 Alunos | ✅ Excelente | CRUD completo, filtros eficientes |
| 🥋 Turmas | ✅ Excelente | Horários, dias, ativação |
| ✅ Presenças | ✅ Muito Bom | Check-in por turma, relatórios |
| 🎓 Graduações | ✅ Muito Bom | Timeline, promoções |
| 💰 Pagamentos | ⚠️ Bom* | *Funciona mas precisa validação |
| 📊 Dashboard | ⚠️ Regular | Falta separar métricas |
| 🔔 Notificações | ⚠️ Regular | Cálculo de atraso com bug |

---

## 🎯 AÇÕES IMEDIATAS (Esta Semana)

### Para o CLIENTE:

- [ ] **Reunião de Validação** (30-45 min)
  - Validar regras de vencimento (10/15/25)
  - Validar carência de 3 dias
  - Validar antecedência de cobrança
  - Definir regra de ausências
  - Definir obrigatoriedade de responsável
  - Definir fluxo de geração de pagamentos

### Para a EQUIPE TÉCNICA:

- [ ] **Atualizar Documentação**
  - FIRESTORE_SCHEMA.md
  - IMPLEMENTACAO_MVP.md
  - README.md

- [ ] **Corrigir Bugs Críticos**
  - NotificationService (cálculo atraso)
  - Dashboard (separar métricas)
  - Formulário (adicionar devedor)

- [ ] **Criar Script Migração**
  - Atualizar pagamentos antigos
  - Adicionar campos novos
  - Recalcular status

- [ ] **Testes End-to-End**
  - Testar fluxo completo de pagamento
  - Testar transições de status
  - Validar cálculos de datas

---

## 💡 SUGESTÕES VALIOSAS

### Funcionalidades Futuras (Após MVP):

1. **Notificações Automáticas**
   - WhatsApp: "Olá [Nome], sua mensalidade vence dia [X]"
   - Email: Lembrete 3 dias antes do vencimento
   - SMS: Alerta de atraso

2. **Integração Pagamento**
   - PIX com QR Code
   - Link de pagamento online
   - Boleto bancário

3. **Relatórios Gerenciais**
   - Projeção de receita mensal
   - Taxa de evasão (%)
   - Análise de frequência por turma

4. **App para Aluno**
   - Consultar pagamentos
   - Marcar presença (QR Code)
   - Ver próximas aulas

---

## 📊 SCORECARD DO SISTEMA

```
Funcionalidade:     ████████░░ 85%
Usabilidade:        █████████░ 90%
Documentação:       ████░░░░░░ 40%  ⚠️
Testes:             ██████░░░░ 60%
Performance:        ████████░░ 85%
Segurança:          ███████░░░ 75%

GERAL:              ███████░░░ 72%  ⚠️
```

**Meta para Produção:** 90%+

**Tempo Estimado para 90%:** 3-5 dias úteis
- 1 dia: Validação + Documentação
- 1 dia: Correções de bugs
- 1 dia: Script migração + Testes
- 1-2 dias: Buffer/ajustes

---

## 🚦 SEMÁFORO DE DECISÃO

### 🟢 PODE IR PARA PRODUÇÃO SE:
- [ ] Cliente validar regras de negócio
- [ ] Bugs críticos corrigidos
- [ ] Documentação atualizada
- [ ] Dados antigos migrados

### 🟡 CAUTELA - Pode usar com ressalvas:
- Funciona mas pode precisar ajustes
- Monitorar feedback dos usuários
- Ter plano de rollback

### 🔴 NÃO PODE IR - Bloqueadores:
- ❌ Cálculos financeiros errados
- ❌ Perda de dados
- ❌ Regras não validadas

**Status Atual:** 🟡 CAUTELA  
**Após correções:** 🟢 APROVADO

---

## 📞 PRÓXIMOS PASSOS

1. **Agendar Reunião de Validação**
   - Participantes: Cliente + Desenvolvedor
   - Duração: 30-45 minutos
   - Objetivo: Validar regras de negócio

2. **Implementar Correções**
   - Seguir prioridades do relatório completo
   - Commit após cada correção
   - Testar incrementalmente

3. **Preparar para Produção**
   - Ambiente de homologação
   - Treinamento de usuários
   - Documentação de suporte

4. **Go Live**
   - Migração de dados
   - Monitoramento
   - Suporte inicial

---

**📎 Documento Completo:** Ver `ANALISE_REQUISITOS_COMPLETA.md`

**Última Atualização:** 20/11/2025  
**Próxima Revisão:** Após validação do cliente
